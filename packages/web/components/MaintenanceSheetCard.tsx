/**
 * @fileoverview UC0 / UC0.1 / UC0.5 F-35 ODIN/ALIS Maintenance Spreadsheet Card (`MaintenanceSheetCard.tsx`).
 *
 * Renders an Excel / Google Sheets-like interactive maintenance grid for
 * `@F35-Maintenance-Data` (`f35_maintenance_data_agent`) backed by the F35 Datawarehouse
 * in BigQuery `EU`:
 * - **UC 0 (`maintenance_work_orders`)**: Work order log explorer and MICAP readiness triage.
 * - **UC 0.1 (`phm_bit_fault_events`)**: 1553 Multiplex Bus PHM/BIT fault event triage and
 *   Could Not Duplicate (`CND (Repeat)`) anomaly detection.
 * - **UC 0.5 (`work_center_tooling_and_sqep`)**: Multi-table SQL join across work orders,
 *   PHM/BIT fault logs, calibrated support tooling, and SQEP / QAR shift dispatch readiness.
 *
 * Features:
 * - Top spreadsheet toolbar with sheet title, row/column count badge, EU BigQuery
 *   execution source & latency badge, source/joined table badges (`maintenance_work_orders`,
 *   `phm_bit_fault_events`, `work_center_tooling_and_sqep`), and a clickable
 *   `[📥 Download .CSV (Excel / Google Sheets)]` anchor tag bound to `csv_download_url`.
 * - Formula bar (`fx`) displaying the executed read-only SQL query or active cell formula.
 * - Dual-row Excel/Google Sheets column header with column letters (`A`, `B`, `C`... `Z`)
 *   above field display labels and semantic description tooltips (`title={col.description}`).
 * - Numbered row gutter (`1`, `2`, `3`...), colour-coded status pills for:
 *   - `aircraft_status`: `🟢 FMC`, `🟡 PMC-M`, `🟠 NMC-M`, `🔴 NMC-S (MICAP)`
 *   - `fault_severity` (UC 0.1): `🔴 CRITICAL_GROUNDING`, `🟠 DEGRADED_PMC`, `🟡 ADVISORY_PHM`, `⚪ NO_BIT_FAULT_LOGGED`
 *   - `cnd_flag` (UC 0.1): `⚠️ CND (Repeat)` vs `✅ Verified`
 *   - `tool_calibration_status` (UC 0.5): `🟢 CALIBRATED_SERVICEABLE`, `🟡 CALIBRATION_DUE_WARNING`, `🔴 EXPIRED_OUT_OF_CAL`, `🟠 IN_USE_OTHER_BAY`
 *   - `bay_dispatch_status` (UC 0.5): `🟢 READY_TO_DISPATCH`, `🔴 BLOCKED_TOOL_OUT_OF_CAL`, `🟠 BLOCKED_NO_QAR_ON_SHIFT`, `🔴 BLOCKED_AWAITING_MICAP_PART`
 * - Sticky `∑ FX` formula summary footer row (`=COUNTA(...)`, `=SUM(logged_man_hours)`,
 *   `=AVERAGE(estimated_mttr_hours)`, `=COUNTIF(..., "NMC-S")`, plus optional UC 0.1 / UC 0.5 formulas).
 */

import {
  React as VegaReact,
  type VNodeElement,
  type VNode,
  type VNodeChild,
} from "./VegaCanvas";

export namespace React {
  export type FC<P = Record<string, unknown>> = (props: P) => VNodeElement;
}
export const React = VegaReact;

export type { VNodeElement, VNode, VNodeChild };

/**
 * Canonical F35 Datawarehouse table names supported by `@F35-Maintenance-Data` (UC 0, UC 0.1, UC 0.5).
 */
export const F35_WAREHOUSE_TABLES = [
  "maintenance_work_orders",
  "phm_bit_fault_events",
  "work_center_tooling_and_sqep",
] as const;

export type F35WarehouseTableName = (typeof F35_WAREHOUSE_TABLES)[number];

export interface WarehouseTableBadgeMeta {
  tableName: F35WarehouseTableName | string;
  label: string;
  useCase: string;
  description: string;
}

/**
 * Metadata and display badges for the three UC 0 / UC 0.1 / UC 0.5 F35 Datawarehouse tables.
 */
export const F35_WAREHOUSE_TABLE_BADGES: Readonly<
  Record<string, WarehouseTableBadgeMeta>
> = Object.freeze({
  maintenance_work_orders: {
    tableName: "maintenance_work_orders",
    label: "📋 maintenance_work_orders",
    useCase: "UC 0",
    description: "Table 7: F-35 ODIN/ALIS Maintenance Work Orders",
  },
  phm_bit_fault_events: {
    tableName: "phm_bit_fault_events",
    label: "⚡ phm_bit_fault_events",
    useCase: "UC 0.1",
    description:
      "Table 8: PHM / 1553 Multiplex Bus BIT Fault Events & CND Triage",
  },
  work_center_tooling_and_sqep: {
    tableName: "work_center_tooling_and_sqep",
    label: "🛠️ work_center_tooling_and_sqep",
    useCase: "UC 0.5",
    description:
      "Table 9: Work Center Calibrated Support Equipment & SQEP Shift Roster",
  },
});

/**
 * Visual color tone for status pills in `MaintenanceSheetCard`.
 */
export type StatusBadgeTone =
  | "green"
  | "amber"
  | "orange"
  | "red"
  | "yellow-blue"
  | "slate";

/**
 * Column metadata for the Excel / Google Sheets-like Maintenance Card.
 * Mirrors `SpreadsheetColumnHeader` in `app/schemas.py`.
 */
export interface SpreadsheetColumnHeader {
  /** Excel/Sheets column letter (`A`..`Z`). */
  col_letter: string;
  /** Optional alias matching backend `column_letter`. */
  column_letter?: string;
  /** Underlying BigQuery column name (`work_order_id`, `tail_number`, `fault_severity`, etc.). */
  field_name: string;
  /** Human-friendly column header label. */
  display_label: string;
  /** BigQuery SQL data type (`STRING`, `FLOAT64`, `INT64`, `BOOLEAN`, `TIMESTAMP`). */
  data_type: string;
  /** Semantic column description surfaced as header tooltip (`title`). */
  description: string;
}

/**
 * Spreadsheet formula summary footer row (`∑ FX`).
 * Mirrors `SpreadsheetFormulaFooter` in `app/schemas.py`.
 */
export interface SpreadsheetFormulaFooter {
  /** Row count formula expression, e.g., `=COUNTA(A2:A13) -> 12 Work Orders`. */
  row_count_formula: string;
  /** Total logged man-hours formula expression, e.g., `=SUM(logged_man_hours) -> 163.0 hrs`. */
  total_man_hours_formula: string;
  /** Mean time to repair formula expression, e.g., `=AVERAGE(estimated_mttr_hours) -> 9.88 hrs`. */
  avg_mttr_hours_formula: string;
  /** Supply-critical MICAP count formula expression, e.g., `=COUNTIF(aircraft_status, "NMC-S") -> 2 MICAP`. */
  micap_count_formula: string;
  /** Optional UC 0.1 CND repeat count formula expression. */
  cnd_repeat_count_formula?: string;
  /** Optional UC 0.1 critical grounding fault count formula expression. */
  critical_fault_count_formula?: string;
  /** Optional UC 0.5 out-of-calibration tool count formula expression. */
  expired_tool_count_formula?: string;
  /** Optional UC 0.5 blocked bay dispatch count formula expression. */
  blocked_bay_count_formula?: string;
  [key: string]: unknown;
}

/**
 * Props for `MaintenanceSheetCard`, matching the `MaintenanceSpreadsheetCard`
 * Pydantic model returned by `execute_maintenance_sql` (`app/tools/uc0_maintenance.py`).
 */
export interface MaintenanceSpreadsheetCardProps {
  /** Unique spreadsheet card identifier (`SHEET-ODIN-...`). */
  sheet_id: string;
  /** Spreadsheet workbook / tab title. */
  sheet_title: string;
  /** Validated read-only BigQuery `SELECT` query executed for this card. */
  executed_sql: string;
  /** Execution source (`bigquery_eu_live`, `BIGQUERY_EU`, or deterministic EU seed fallback). */
  execution_source: string;
  /** Query execution and card serialization latency in milliseconds. */
  execution_latency_ms: number;
  /** Total number of rows returned. */
  row_count: number;
  /** Ordered column definitions with Excel letters (`A`..`Z`) and semantic tooltips. */
  columns: SpreadsheetColumnHeader[];
  /** Returned rows keyed by BigQuery column `field_name`. */
  rows: Array<Record<string, unknown>>;
  /** Sticky `∑ FX` formula summary footer evaluations. */
  formula_footer: SpreadsheetFormulaFooter;
  /** Cloud Storage URI where the `.csv` export is stored (`gs://antig-dave-f35-staging-europe-west1/exports/...`). */
  csv_gcs_uri: string;
  /** Authenticated browser download link (`https://storage.cloud.google.com/antig-dave-f35-staging-europe-west1/exports/...`). */
  csv_download_url: string;
  /** Optional active cell formula override for the `fx` formula bar. */
  active_cell_formula?: string;
  /** Optional primary table FQN or comma-separated joined table list. */
  table_fqn?: string;
  /** Optional list of source / joined F35 Datawarehouse tables referenced by the SQL query. */
  source_tables?: string[];
  /** Optional alias for `source_tables`. */
  referenced_tables?: string[];
  /** Optional alias for joined tables when a query spans multiple tables. */
  joined_tables?: string[];
  /** Optional alias for tables used in the query. */
  tables_used?: string[];
}

/** Alias matching backend `MaintenanceSpreadsheetCard` model name. */
export type MaintenanceSpreadsheetCard = MaintenanceSpreadsheetCardProps;

/**
 * UC 0 (`maintenance_work_orders`): Aircraft readiness status badges.
 */
export const AIRCRAFT_STATUS_BADGES: Readonly<Record<string, string>> =
  Object.freeze({
    FMC: "🟢 FMC",
    "PMC-M": "🟡 PMC-M",
    "NMC-M": "🟠 NMC-M",
    "NMC-S": "🔴 NMC-S (MICAP)",
    "NMC-S (MICAP)": "🔴 NMC-S (MICAP)",
  });

/**
 * UC 0.1 (`phm_bit_fault_events`): PHM / 1553 BIT fault severity badges.
 * - `CRITICAL_GROUNDING` (red)
 * - `DEGRADED_PMC` (amber/orange)
 * - `ADVISORY_PHM` (yellow/blue)
 * - `NO_BIT_FAULT_LOGGED` (slate/neutral)
 */
export const FAULT_SEVERITY_BADGES: Readonly<Record<string, string>> =
  Object.freeze({
    CRITICAL_GROUNDING: "🔴 CRITICAL_GROUNDING",
    DEGRADED_PMC: "🟠 DEGRADED_PMC",
    ADVISORY_PHM: "🟡 ADVISORY_PHM",
    NO_BIT_FAULT_LOGGED: "⚪ NO_BIT_FAULT_LOGGED",
  });

/**
 * UC 0.1 (`phm_bit_fault_events`): Could Not Duplicate (`cnd_flag`) repeat warning vs verified badges.
 */
export const CND_FLAG_BADGES: Readonly<Record<string, string>> = Object.freeze({
  TRUE: "⚠️ CND (Repeat)",
  "1": "⚠️ CND (Repeat)",
  CND: "⚠️ CND (Repeat)",
  "CND (REPEAT)": "⚠️ CND (Repeat)",
  "CND (Repeat)": "⚠️ CND (Repeat)",
  FALSE: "✅ Verified",
  "0": "✅ Verified",
  VERIFIED: "✅ Verified",
  Verified: "✅ Verified",
});

/**
 * UC 0.5 (`work_center_tooling_and_sqep`): Support equipment tool calibration status badges.
 * - `CALIBRATED_SERVICEABLE` (green)
 * - `CALIBRATION_DUE_WARNING` (amber)
 * - `EXPIRED_OUT_OF_CAL` (red)
 * - `IN_USE_OTHER_BAY` (orange)
 */
export const TOOL_CALIBRATION_STATUS_BADGES: Readonly<Record<string, string>> =
  Object.freeze({
    CALIBRATED_SERVICEABLE: "🟢 CALIBRATED_SERVICEABLE",
    CALIBRATION_DUE_WARNING: "🟡 CALIBRATION_DUE_WARNING",
    EXPIRED_OUT_OF_CAL: "🔴 EXPIRED_OUT_OF_CAL",
    IN_USE_OTHER_BAY: "🟠 IN_USE_OTHER_BAY",
  });

/**
 * UC 0.5 (`work_center_tooling_and_sqep`): Maintenance bay dispatch readiness status badges.
 * - `READY_TO_DISPATCH` (green)
 * - `BLOCKED_TOOL_OUT_OF_CAL` (red)
 * - `BLOCKED_NO_QAR_ON_SHIFT` (orange)
 * - `BLOCKED_AWAITING_MICAP_PART` (red)
 */
export const BAY_DISPATCH_STATUS_BADGES: Readonly<Record<string, string>> =
  Object.freeze({
    READY_TO_DISPATCH: "🟢 READY_TO_DISPATCH",
    BLOCKED_TOOL_OUT_OF_CAL: "🔴 BLOCKED_TOOL_OUT_OF_CAL",
    BLOCKED_NO_QAR_ON_SHIFT: "🟠 BLOCKED_NO_QAR_ON_SHIFT",
    BLOCKED_AWAITING_MICAP_PART: "🔴 BLOCKED_AWAITING_MICAP_PART",
  });

/**
 * Authoritative combined mapping of all F-35 ODIN/ALIS status, PHM/BIT fault severity,
 * CND flag, tool calibration, and bay dispatch codes to colour-coded spreadsheet badges.
 */
export const MAINTENANCE_STATUS_BADGES: Readonly<Record<string, string>> =
  Object.freeze({
    ...AIRCRAFT_STATUS_BADGES,
    ...FAULT_SEVERITY_BADGES,
    ...CND_FLAG_BADGES,
    ...TOOL_CALIBRATION_STATUS_BADGES,
    ...BAY_DISPATCH_STATUS_BADGES,
  });

/**
 * Set of column `field_name` values that render as colour-coded status pills.
 */
export const STATUS_BADGE_FIELD_NAMES: ReadonlySet<string> = new Set([
  "aircraft_status",
  "fault_severity",
  "cnd_flag",
  "tool_calibration_status",
  "bay_dispatch_status",
]);

/**
 * Scoped stylesheet for the Excel / Google Sheets-like `MaintenanceSheetCard` component.
 */
export const MAINTENANCE_SHEET_CARD_STYLES = `
.f35-sheet-card {
  font-family: "Inter", "Roboto", -apple-system, BlinkMacSystemFont, sans-serif;
  background: #0f172a;
  color: #e2e8f0;
  border: 1px solid #334155;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.45);
}
.f35-sheet-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 16px;
  background: linear-gradient(90deg, #0f172a 0%, #1e293b 100%);
  border-bottom: 1px solid #334155;
}
.f35-sheet-toolbar-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}
.f35-sheet-table-badges {
  display: inline-flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
}
.f35-sheet-badge {
  display: inline-flex;
  align-items: center;
  padding: 3px 9px;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 600;
  background: #1e293b;
  color: #94a3b8;
  border: 1px solid #475569;
}
.f35-sheet-table-badge {
  background: #0f172a;
  color: #bae6fd;
  border-color: #0284c7;
  font-family: "JetBrains Mono", "Fira Code", monospace;
  font-size: 11px;
}
.f35-sheet-join-badge {
  background: rgba(14, 165, 233, 0.16);
  color: #38bdf8;
  border-color: #0ea5e9;
  font-weight: 700;
}
.f35-sheet-csv-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 700;
  color: #ecfdf5;
  background: #059669;
  border: 1px solid #10b981;
  text-decoration: none;
}
.f35-sheet-formula-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 16px;
  background: #020617;
  border-bottom: 1px solid #334155;
  font-family: "JetBrains Mono", "Fira Code", monospace;
  font-size: 12px;
}
.f35-sheet-fx-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 2px 8px;
  border-radius: 4px;
  background: #1e293b;
  color: #38bdf8;
  font-style: italic;
  font-weight: 700;
}
.f35-sheet-grid-scroll {
  overflow-x: auto;
  max-width: 100%;
  container-type: inline-size;
}
.f35-sheet-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}
.f35-sheet-table thead {
  position: sticky;
  inset-block-start: 0;
  z-index: 1;
}
.f35-sheet-col-letter {
  background: #1e293b;
  color: #94a3b8;
  font-family: "JetBrains Mono", monospace;
  font-size: 11px;
  font-weight: 700;
  text-align: center;
  padding: 4px 8px;
  border: 1px solid #334155;
}
.f35-sheet-col-field {
  background: #0f172a;
  color: #f8fafc;
  font-weight: 600;
  text-align: left;
  padding: 6px 10px;
  border: 1px solid #334155;
  white-space: nowrap;
}
.f35-sheet-row-gutter {
  background: #1e293b;
  color: #64748b;
  font-family: "JetBrains Mono", monospace;
  font-size: 11px;
  font-weight: 600;
  text-align: center;
  padding: 6px 8px;
  border: 1px solid #334155;
  user-select: none;
}
.f35-sheet-cell {
  padding: 6px 10px;
  border: 1px solid #1e293b;
  color: #e2e8f0;
  white-space: nowrap;
}
.f35-sheet-status-pill {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: 9999px;
  font-size: 11px;
  font-weight: 700;
}
.f35-sheet-status-pill--green {
  background: rgba(16, 185, 129, 0.15);
  color: #6ee7b7;
  border: 1px solid rgba(16, 185, 129, 0.4);
}
.f35-sheet-status-pill--amber {
  background: rgba(245, 158, 11, 0.15);
  color: #fcd34d;
  border: 1px solid rgba(245, 158, 11, 0.4);
}
.f35-sheet-status-pill--orange {
  background: rgba(249, 115, 22, 0.15);
  color: #fdba74;
  border: 1px solid rgba(249, 115, 22, 0.45);
}
.f35-sheet-status-pill--red {
  background: rgba(239, 68, 68, 0.18);
  color: #fca5a5;
  border: 1px solid rgba(239, 68, 68, 0.5);
}
.f35-sheet-status-pill--yellow-blue {
  background: rgba(56, 189, 248, 0.15);
  color: #fde047;
  border: 1px solid rgba(56, 189, 248, 0.45);
}
.f35-sheet-status-pill--slate {
  background: rgba(148, 163, 184, 0.14);
  color: #cbd5e1;
  border: 1px solid rgba(148, 163, 184, 0.35);
}
.f35-sheet-footer-row {
  position: sticky;
  bottom: 0;
  background: #020617;
  color: #38bdf8;
  font-family: "JetBrains Mono", monospace;
  font-size: 11px;
  font-weight: 600;
  border-top: 2px solid #475569;
}
`.trim();

/**
 * Formats a UC 0.1 `fault_severity` value (`phm_bit_fault_events`) into its canonical badge:
 * - `"CRITICAL_GROUNDING"` -> `"🔴 CRITICAL_GROUNDING"`
 * - `"DEGRADED_PMC"` -> `"🟠 DEGRADED_PMC"`
 * - `"ADVISORY_PHM"` -> `"🟡 ADVISORY_PHM"`
 * - `"NO_BIT_FAULT_LOGGED"` -> `"⚪ NO_BIT_FAULT_LOGGED"`
 */
export function formatFaultSeverityBadge(severity: unknown): string {
  const normalized = String(severity ?? "").trim();
  const stripped = normalized.replace(/^[🔴🟠🟡🔵⚪⚫]\s*/u, "").trim();
  const upper = stripped.toUpperCase();

  if (upper === "CRITICAL_GROUNDING") {
    return "🔴 CRITICAL_GROUNDING";
  }
  if (upper === "DEGRADED_PMC") {
    return "🟠 DEGRADED_PMC";
  }
  if (upper === "ADVISORY_PHM") {
    return "🟡 ADVISORY_PHM";
  }
  if (upper === "NO_BIT_FAULT_LOGGED") {
    return "⚪ NO_BIT_FAULT_LOGGED";
  }
  return normalized || "⚪ NO_BIT_FAULT_LOGGED";
}

/**
 * Formats a UC 0.1 `cnd_flag` value (`phm_bit_fault_events`) into a `CND (Repeat)`
 * warning badge vs `Verified` badge:
 * - `true` / `1` / `"TRUE"` / `"CND"` / `"CND (Repeat)"` -> `"⚠️ CND (Repeat)"`
 * - `false` / `0` / `"FALSE"` / `"Verified"` -> `"✅ Verified"`
 */
export function formatCndFlagBadge(cndFlag: unknown): string {
  if (typeof cndFlag === "boolean") {
    return cndFlag ? "⚠️ CND (Repeat)" : "✅ Verified";
  }
  if (typeof cndFlag === "number") {
    return cndFlag !== 0 ? "⚠️ CND (Repeat)" : "✅ Verified";
  }
  const normalized = String(cndFlag ?? "").trim();
  const stripped = normalized.replace(/^[⚠️✅🔴🟡🟢⚪]\s*/u, "").trim();
  const upper = stripped.toUpperCase();

  if (
    upper === "TRUE" ||
    upper === "1" ||
    upper === "YES" ||
    upper === "CND" ||
    upper === "CND_REPEAT" ||
    upper === "CND (REPEAT)" ||
    upper.includes("CND")
  ) {
    return "⚠️ CND (Repeat)";
  }
  if (
    upper === "FALSE" ||
    upper === "0" ||
    upper === "NO" ||
    upper === "VERIFIED" ||
    upper === "CONFIRMED" ||
    upper.includes("VERIFIED")
  ) {
    return "✅ Verified";
  }
  return normalized || "✅ Verified";
}

/**
 * Formats a UC 0.5 `tool_calibration_status` value (`work_center_tooling_and_sqep`)
 * into its canonical badge:
 * - `"CALIBRATED_SERVICEABLE"` -> `"🟢 CALIBRATED_SERVICEABLE"`
 * - `"CALIBRATION_DUE_WARNING"` -> `"🟡 CALIBRATION_DUE_WARNING"`
 * - `"EXPIRED_OUT_OF_CAL"` -> `"🔴 EXPIRED_OUT_OF_CAL"`
 * - `"IN_USE_OTHER_BAY"` -> `"🟠 IN_USE_OTHER_BAY"`
 */
export function formatToolCalibrationBadge(status: unknown): string {
  const normalized = String(status ?? "").trim();
  const stripped = normalized.replace(/^[🟢🟡🔴🟠⚪]\s*/u, "").trim();
  const upper = stripped.toUpperCase();

  if (upper === "CALIBRATED_SERVICEABLE") {
    return "🟢 CALIBRATED_SERVICEABLE";
  }
  if (upper === "CALIBRATION_DUE_WARNING") {
    return "🟡 CALIBRATION_DUE_WARNING";
  }
  if (upper === "EXPIRED_OUT_OF_CAL") {
    return "🔴 EXPIRED_OUT_OF_CAL";
  }
  if (upper === "IN_USE_OTHER_BAY") {
    return "🟠 IN_USE_OTHER_BAY";
  }
  return normalized || "⚪ UNKNOWN";
}

/**
 * Formats a UC 0.5 `bay_dispatch_status` value (`work_center_tooling_and_sqep`)
 * into its canonical badge:
 * - `"READY_TO_DISPATCH"` -> `"🟢 READY_TO_DISPATCH"`
 * - `"BLOCKED_TOOL_OUT_OF_CAL"` -> `"🔴 BLOCKED_TOOL_OUT_OF_CAL"`
 * - `"BLOCKED_NO_QAR_ON_SHIFT"` -> `"🟠 BLOCKED_NO_QAR_ON_SHIFT"`
 * - `"BLOCKED_AWAITING_MICAP_PART"` -> `"🔴 BLOCKED_AWAITING_MICAP_PART"`
 */
export function formatBayDispatchBadge(status: unknown): string {
  const normalized = String(status ?? "").trim();
  const stripped = normalized.replace(/^[🟢🟡🔴🟠⚪]\s*/u, "").trim();
  const upper = stripped.toUpperCase();

  if (upper === "READY_TO_DISPATCH") {
    return "🟢 READY_TO_DISPATCH";
  }
  if (upper === "BLOCKED_TOOL_OUT_OF_CAL") {
    return "🔴 BLOCKED_TOOL_OUT_OF_CAL";
  }
  if (upper === "BLOCKED_NO_QAR_ON_SHIFT") {
    return "🟠 BLOCKED_NO_QAR_ON_SHIFT";
  }
  if (upper === "BLOCKED_AWAITING_MICAP_PART") {
    return "🔴 BLOCKED_AWAITING_MICAP_PART";
  }
  return normalized || "⚪ UNKNOWN";
}

/**
 * Formats an F-35 status or triage code across UC 0 (`aircraft_status`),
 * UC 0.1 (`fault_severity`, `cnd_flag`), and UC 0.5 (`tool_calibration_status`,
 * `bay_dispatch_status`) into its canonical colour-coded spreadsheet status badge:
 *
 * - `aircraft_status`:
 *   - `"FMC"` -> `"🟢 FMC"`
 *   - `"PMC-M"` -> `"🟡 PMC-M"`
 *   - `"NMC-M"` -> `"🟠 NMC-M"`
 *   - `"NMC-S"` / `"NMC-S (MICAP)"` -> `"🔴 NMC-S (MICAP)"`
 * - `fault_severity` (UC 0.1):
 *   - `"CRITICAL_GROUNDING"` -> `"🔴 CRITICAL_GROUNDING"`
 *   - `"DEGRADED_PMC"` -> `"🟠 DEGRADED_PMC"`
 *   - `"ADVISORY_PHM"` -> `"🟡 ADVISORY_PHM"`
 *   - `"NO_BIT_FAULT_LOGGED"` -> `"⚪ NO_BIT_FAULT_LOGGED"`
 * - `cnd_flag` (UC 0.1):
 *   - `true` / `"CND (Repeat)"` -> `"⚠️ CND (Repeat)"`
 *   - `false` / `"Verified"` -> `"✅ Verified"`
 * - `tool_calibration_status` (UC 0.5):
 *   - `"CALIBRATED_SERVICEABLE"` -> `"🟢 CALIBRATED_SERVICEABLE"`
 *   - `"CALIBRATION_DUE_WARNING"` -> `"🟡 CALIBRATION_DUE_WARNING"`
 *   - `"EXPIRED_OUT_OF_CAL"` -> `"🔴 EXPIRED_OUT_OF_CAL"`
 *   - `"IN_USE_OTHER_BAY"` -> `"🟠 IN_USE_OTHER_BAY"`
 * - `bay_dispatch_status` (UC 0.5):
 *   - `"READY_TO_DISPATCH"` -> `"🟢 READY_TO_DISPATCH"`
 *   - `"BLOCKED_TOOL_OUT_OF_CAL"` -> `"🔴 BLOCKED_TOOL_OUT_OF_CAL"`
 *   - `"BLOCKED_NO_QAR_ON_SHIFT"` -> `"🟠 BLOCKED_NO_QAR_ON_SHIFT"`
 *   - `"BLOCKED_AWAITING_MICAP_PART"` -> `"🔴 BLOCKED_AWAITING_MICAP_PART"`
 */
export function formatStatusBadge(
  status: unknown,
  fieldName?: string
): string {
  const normalizedField = String(fieldName ?? "")
    .trim()
    .toLowerCase();

  if (normalizedField === "cnd_flag" || typeof status === "boolean") {
    return formatCndFlagBadge(status);
  }
  if (normalizedField === "fault_severity") {
    return formatFaultSeverityBadge(status);
  }
  if (normalizedField === "tool_calibration_status") {
    return formatToolCalibrationBadge(status);
  }
  if (normalizedField === "bay_dispatch_status") {
    return formatBayDispatchBadge(status);
  }

  const normalized = String(status ?? "").trim();
  const stripped = normalized
    .replace(/^[🟢🟡🟠🔴🔵⚪⚫⚠️✅]\s*/u, "")
    .trim();
  const upper = stripped.toUpperCase();

  // UC 0: aircraft_status
  if (upper === "FMC") {
    return "🟢 FMC";
  }
  if (upper === "PMC-M") {
    return "🟡 PMC-M";
  }
  if (upper === "NMC-M") {
    return "🟠 NMC-M";
  }
  if (upper === "NMC-S" || upper === "NMC-S (MICAP)") {
    return "🔴 NMC-S (MICAP)";
  }

  // UC 0.1: fault_severity
  if (
    upper === "CRITICAL_GROUNDING" ||
    upper === "DEGRADED_PMC" ||
    upper === "ADVISORY_PHM" ||
    upper === "NO_BIT_FAULT_LOGGED"
  ) {
    return formatFaultSeverityBadge(stripped);
  }

  // UC 0.1: cnd_flag
  if (
    upper === "CND" ||
    upper === "CND (REPEAT)" ||
    upper === "CND_REPEAT" ||
    upper === "VERIFIED" ||
    upper === "TRUE" ||
    upper === "FALSE"
  ) {
    return formatCndFlagBadge(stripped);
  }

  // UC 0.5: tool_calibration_status
  if (
    upper === "CALIBRATED_SERVICEABLE" ||
    upper === "CALIBRATION_DUE_WARNING" ||
    upper === "EXPIRED_OUT_OF_CAL" ||
    upper === "IN_USE_OTHER_BAY"
  ) {
    return formatToolCalibrationBadge(stripped);
  }

  // UC 0.5: bay_dispatch_status
  if (
    upper === "READY_TO_DISPATCH" ||
    upper === "BLOCKED_TOOL_OUT_OF_CAL" ||
    upper === "BLOCKED_NO_QAR_ON_SHIFT" ||
    upper === "BLOCKED_AWAITING_MICAP_PART"
  ) {
    return formatBayDispatchBadge(stripped);
  }

  return normalized || "⚪ UNKNOWN";
}

/**
 * Resolves the semantic visual tone (`green`, `amber`, `orange`, `red`, `yellow-blue`, `slate`)
 * for a status or triage value.
 */
export function resolveStatusBadgeTone(
  rawValue: unknown,
  fieldName?: string
): StatusBadgeTone {
  const badge = formatStatusBadge(rawValue, fieldName);
  const stripped = badge.replace(/^[🟢🟡🟠🔴🔵⚪⚫⚠️✅]\s*/u, "").trim();
  const upper = stripped.toUpperCase();

  if (
    upper === "NMC-S" ||
    upper === "NMC-S (MICAP)" ||
    upper === "CRITICAL_GROUNDING" ||
    upper === "EXPIRED_OUT_OF_CAL" ||
    upper === "BLOCKED_TOOL_OUT_OF_CAL" ||
    upper === "BLOCKED_AWAITING_MICAP_PART"
  ) {
    return "red";
  }
  if (
    upper === "NMC-M" ||
    upper === "DEGRADED_PMC" ||
    upper === "IN_USE_OTHER_BAY" ||
    upper === "BLOCKED_NO_QAR_ON_SHIFT" ||
    upper === "CND (REPEAT)"
  ) {
    return "orange";
  }
  if (upper === "ADVISORY_PHM") {
    return "yellow-blue";
  }
  if (upper === "PMC-M" || upper === "CALIBRATION_DUE_WARNING") {
    return "amber";
  }
  if (
    upper === "FMC" ||
    upper === "CALIBRATED_SERVICEABLE" ||
    upper === "READY_TO_DISPATCH" ||
    upper === "VERIFIED"
  ) {
    return "green";
  }
  return "slate";
}

function normalizeTableToken(rawToken: string): string {
  const cleaned = rawToken
    .replace(/[`"'\s]/g, "")
    .trim();
  if (!cleaned) {
    return "";
  }
  const parts = cleaned.split(".");
  return (parts[parts.length - 1] ?? "").toLowerCase();
}

/**
 * Extracts the ordered list of F35 Datawarehouse tables referenced by a
 * `MaintenanceSpreadsheetCard` via explicit props (`source_tables`, `referenced_tables`,
 * `joined_tables`, `tables_used`, `table_fqn`) and/or SQL inspection (`executed_sql`).
 */
export function resolveReferencedTables(
  props: Pick<
    MaintenanceSpreadsheetCardProps,
    | "executed_sql"
    | "table_fqn"
    | "source_tables"
    | "referenced_tables"
    | "joined_tables"
    | "tables_used"
  >
): string[] {
  const discovered: string[] = [];
  const addTable = (candidate: string): void => {
    const norm = normalizeTableToken(candidate);
    if (norm && !discovered.includes(norm)) {
      discovered.push(norm);
    }
  };

  const explicitLists = [
    props.source_tables,
    props.referenced_tables,
    props.joined_tables,
    props.tables_used,
  ];
  for (const list of explicitLists) {
    if (Array.isArray(list)) {
      for (const item of list) {
        if (typeof item === "string") {
          addTable(item);
        }
      }
    }
  }

  if (typeof props.table_fqn === "string" && props.table_fqn.trim()) {
    for (const part of props.table_fqn.split(/[,+⋈]/)) {
      addTable(part);
    }
  }

  const sqlText = String(props.executed_sql ?? "");
  if (sqlText) {
    const matches: Array<{ table: string; index: number }> = [];
    for (const table of F35_WAREHOUSE_TABLES) {
      const regex = new RegExp(`\\b${table}\\b`, "i");
      const match = regex.exec(sqlText);
      if (match) {
        matches.push({ table, index: match.index });
      }
    }
    matches
      .sort((a, b) => a.index - b.index)
      .forEach((m) => addTable(m.table));
  }

  if (discovered.length === 0) {
    discovered.push("maintenance_work_orders");
  }

  return discovered;
}

function indexToColumnLetter(index: number): string {
  let n = index;
  let letter = "";
  while (n >= 0) {
    letter = String.fromCharCode((n % 26) + 65) + letter;
    n = Math.floor(n / 26) - 1;
  }
  return letter;
}

function formatCellValue(fieldName: string, rawValue: unknown): VNodeChild {
  if (rawValue === null || rawValue === undefined || rawValue === "") {
    return "—";
  }
  const normalizedField = fieldName.trim().toLowerCase();
  if (STATUS_BADGE_FIELD_NAMES.has(normalizedField)) {
    const badge = formatStatusBadge(rawValue, normalizedField);
    const tone = resolveStatusBadgeTone(rawValue, normalizedField);
    return React.createElement(
      "span",
      {
        className: `f35-sheet-status-pill f35-sheet-status-pill--${tone}`,
        "data-status-code": String(rawValue),
        "data-status-field": normalizedField,
        "data-badge-tone": tone,
      },
      badge
    );
  }
  if (typeof rawValue === "boolean") {
    return rawValue ? "TRUE" : "FALSE";
  }
  if (
    typeof rawValue === "number" &&
    (normalizedField === "logged_man_hours" ||
      normalizedField === "estimated_mttr_hours")
  ) {
    return rawValue.toFixed(1);
  }
  return String(rawValue);
}

/**
 * Interactive Excel / Google Sheets-like Maintenance Grid (`MaintenanceSheetCard`)
 * for UC 0 (`maintenance_work_orders`), UC 0.1 (`phm_bit_fault_events`), and
 * UC 0.5 (`work_center_tooling_and_sqep` multi-table SQL joins).
 */
export const MaintenanceSheetCard: React.FC<MaintenanceSpreadsheetCardProps> = (
  props: MaintenanceSpreadsheetCardProps
): VNodeElement => {
  const {
    sheet_id,
    sheet_title,
    executed_sql,
    execution_source,
    execution_latency_ms,
    row_count,
    columns = [],
    rows = [],
    formula_footer,
    csv_gcs_uri,
    csv_download_url,
    active_cell_formula,
  } = props;

  const referencedTables = resolveReferencedTables(props);
  const isMultiTableJoin = referencedTables.length > 1;

  const effectiveColumns: SpreadsheetColumnHeader[] =
    columns.length > 0
      ? columns.map((col, idx) => ({
          ...col,
          col_letter:
            col.col_letter || col.column_letter || indexToColumnLetter(idx),
        }))
      : Object.keys(rows[0] ?? {}).map((key, idx) => ({
          col_letter: indexToColumnLetter(idx),
          field_name: key,
          display_label: key,
          data_type: "STRING",
          description: `Column ${key}`,
        }));

  const formulaBarExpression =
    active_cell_formula && active_cell_formula.trim().length > 0
      ? active_cell_formula.trim()
      : executed_sql;

  const tableBadgeElements: VNodeElement[] = referencedTables.map(
    (tableName) => {
      const meta = F35_WAREHOUSE_TABLE_BADGES[tableName] ?? {
        tableName,
        label: `🗄️ ${tableName}`,
        useCase: "UC 0",
        description: `F35 Datawarehouse table ${tableName}`,
      };
      return React.createElement(
        "span",
        {
          key: `table-badge-${tableName}`,
          className: "f35-sheet-badge f35-sheet-table-badge",
          "data-testid": `table-badge-${tableName}`,
          "data-table-name": tableName,
          "data-use-case": meta.useCase,
          title: `${meta.useCase} — ${meta.description}`,
        },
        meta.label
      );
    }
  );

  const letterHeaderCells: VNodeElement[] = [
    React.createElement(
      "th",
      {
        key: "gutter-corner",
        className: "f35-sheet-col-letter",
        scope: "col",
        title: "Spreadsheet Row Index",
      },
      "#"
    ),
    ...effectiveColumns.map((col) =>
      React.createElement(
        "th",
        {
          key: `letter-${col.col_letter}-${col.field_name}`,
          className: "f35-sheet-col-letter",
          scope: "col",
          "data-col-letter": col.col_letter,
          title: `${col.col_letter}: ${col.description}`,
        },
        col.col_letter
      )
    ),
  ];

  const fieldHeaderCells: VNodeElement[] = [
    React.createElement(
      "th",
      {
        key: "gutter-label",
        className: "f35-sheet-col-field",
        scope: "col",
        title: "Row Number (1-indexed)",
      },
      "Row"
    ),
    ...effectiveColumns.map((col) =>
      React.createElement(
        "th",
        {
          key: `field-${col.col_letter}-${col.field_name}`,
          className: "f35-sheet-col-field",
          scope: "col",
          "data-field-name": col.field_name,
          "data-data-type": col.data_type,
          title: col.description,
        },
        `${col.display_label} (${col.field_name})`
      )
    ),
  ];

  const bodyRows: VNodeElement[] = rows.map((row, rowIndex) => {
    const rowNumber = rowIndex + 1;
    const rowPrimaryId = String(
      row.work_order_id ??
        row.fault_event_id ??
        row.tooling_dispatch_id ??
        row.tool_asset_id ??
        `ROW-${rowNumber}`
    );
    const cells: VNodeElement[] = [
      React.createElement(
        "td",
        {
          key: `row-gutter-${rowNumber}`,
          className: "f35-sheet-row-gutter",
          "data-row-number": String(rowNumber),
        },
        String(rowNumber)
      ),
      ...effectiveColumns.map((col) => {
        const cellCoord = `${col.col_letter}${rowNumber + 1}`;
        const rawVal = row[col.field_name];
        return React.createElement(
          "td",
          {
            key: `cell-${cellCoord}`,
            className: "f35-sheet-cell",
            "data-cell-coord": cellCoord,
            "data-field-name": col.field_name,
            title: `${cellCoord} (${col.display_label}): ${String(rawVal ?? "NULL")}`,
          },
          formatCellValue(col.field_name, rawVal)
        );
      }),
    ];

    return React.createElement(
      "tr",
      {
        key: `row-${rowPrimaryId}-${rowNumber}`,
        "data-row-index": String(rowNumber),
        "data-work-order-id": rowPrimaryId,
      },
      cells
    );
  });

  const footerColSpan = Math.max(effectiveColumns.length, 1);

  const footerFormulaSpans: VNodeElement[] = [
    React.createElement(
      "span",
      {
        key: "formula-row-count",
        "data-formula": "COUNTA",
        style: { marginRight: "16px" },
      },
      formula_footer.row_count_formula
    ),
    React.createElement(
      "span",
      {
        key: "formula-sum-hours",
        "data-formula": "SUM(logged_man_hours)",
        style: { marginRight: "16px" },
      },
      formula_footer.total_man_hours_formula
    ),
    React.createElement(
      "span",
      {
        key: "formula-avg-mttr",
        "data-formula": "AVERAGE(estimated_mttr_hours)",
        style: { marginRight: "16px" },
      },
      formula_footer.avg_mttr_hours_formula
    ),
    React.createElement(
      "span",
      {
        key: "formula-micap-count",
        "data-formula": "COUNTIF(aircraft_status, NMC-S)",
        style: { marginRight: "16px" },
      },
      formula_footer.micap_count_formula
    ),
  ];

  if (formula_footer.cnd_repeat_count_formula) {
    footerFormulaSpans.push(
      React.createElement(
        "span",
        {
          key: "formula-cnd-count",
          "data-formula": "COUNTIF(cnd_flag, TRUE)",
          style: { marginRight: "16px" },
        },
        String(formula_footer.cnd_repeat_count_formula)
      )
    );
  }
  if (formula_footer.critical_fault_count_formula) {
    footerFormulaSpans.push(
      React.createElement(
        "span",
        {
          key: "formula-critical-fault-count",
          "data-formula": "COUNTIF(fault_severity, CRITICAL_GROUNDING)",
          style: { marginRight: "16px" },
        },
        String(formula_footer.critical_fault_count_formula)
      )
    );
  }
  if (formula_footer.expired_tool_count_formula) {
    footerFormulaSpans.push(
      React.createElement(
        "span",
        {
          key: "formula-expired-tool-count",
          "data-formula": "COUNTIF(tool_calibration_status, EXPIRED_OUT_OF_CAL)",
          style: { marginRight: "16px" },
        },
        String(formula_footer.expired_tool_count_formula)
      )
    );
  }
  if (formula_footer.blocked_bay_count_formula) {
    footerFormulaSpans.push(
      React.createElement(
        "span",
        {
          key: "formula-blocked-bay-count",
          "data-formula": "COUNTIF(bay_dispatch_status, BLOCKED_*)",
        },
        String(formula_footer.blocked_bay_count_formula)
      )
    );
  }

  return React.createElement(
    "section",
    {
      className: "f35-sheet-card",
      "data-component": "MaintenanceSheetCard",
      "data-sheet-id": sheet_id,
      "data-execution-source": execution_source,
      "data-csv-gcs-uri": csv_gcs_uri,
      "data-source-tables": referencedTables.join(","),
      "data-multi-table-join": String(isMultiTableJoin),
      "aria-label": `Maintenance Spreadsheet Card: ${sheet_title}`,
    },
    React.createElement(
      "style",
      { key: "sheet-styles" },
      MAINTENANCE_SHEET_CARD_STYLES
    ),
    React.createElement(
      "header",
      {
        key: "sheet-toolbar",
        className: "f35-sheet-toolbar",
        "data-testid": "maintenance-sheet-toolbar",
      },
      React.createElement(
        "div",
        { key: "toolbar-left", className: "f35-sheet-toolbar-meta" },
        React.createElement(
          "strong",
          {
            key: "sheet-title",
            className: "f35-sheet-title",
            "data-testid": "sheet-title",
          },
          `📊 ${sheet_title}`
        ),
        React.createElement(
          "span",
          {
            key: "row-col-badge",
            className: "f35-sheet-badge",
            "data-testid": "row-col-count-badge",
          },
          `${row_count} Rows × ${effectiveColumns.length} Columns`
        ),
        React.createElement(
          "span",
          {
            key: "latency-badge",
            className: "f35-sheet-badge",
            "data-testid": "eu-bq-latency-badge",
          },
          `EU BigQuery (${execution_source}) · ${Number(execution_latency_ms).toFixed(1)} ms`
        ),
        React.createElement(
          "div",
          {
            key: "source-table-badges",
            className: "f35-sheet-table-badges",
            "data-testid": "source-table-badges",
          },
          ...(isMultiTableJoin
            ? [
                React.createElement(
                  "span",
                  {
                    key: "multi-table-join-badge",
                    className: "f35-sheet-badge f35-sheet-join-badge",
                    "data-testid": "multi-table-join-badge",
                    "data-joined-tables": referencedTables.join(","),
                    title: `Multi-table SQL Join across ${referencedTables.join(", ")}`,
                  },
                  `🔗 Joined: ${referencedTables.join(" ⋈ ")}`
                ),
              ]
            : []),
          ...tableBadgeElements
        )
      ),
      React.createElement(
        "div",
        { key: "toolbar-right", className: "f35-sheet-toolbar-actions" },
        React.createElement(
          "a",
          {
            key: "csv-download-link",
            className: "f35-sheet-csv-btn",
            href: csv_download_url,
            target: "_blank",
            rel: "noopener noreferrer",
            "data-testid": "csv-download-link",
            "data-gcs-uri": csv_gcs_uri,
            title: `Download CSV export from ${csv_gcs_uri}`,
          },
          "[📥 Download .CSV (Excel / Google Sheets)]"
        )
      )
    ),
    React.createElement(
      "div",
      {
        key: "formula-bar",
        className: "f35-sheet-formula-bar",
        "data-testid": "maintenance-formula-bar",
      },
      React.createElement(
        "span",
        { key: "fx-icon", className: "f35-sheet-fx-pill" },
        "fx"
      ),
      React.createElement(
        "code",
        {
          key: "fx-sql",
          className: "f35-sheet-fx-expression",
          "data-testid": "formula-bar-sql",
        },
        formulaBarExpression
      )
    ),
    React.createElement(
      "div",
      {
        key: "grid-scroll",
        className: "f35-sheet-grid-scroll",
        tabIndex: 0,
        role: "region",
        "aria-label": `${sheet_title} data grid`,
      },
      React.createElement(
        "table",
        {
          key: "sheet-table",
          className: "f35-sheet-table",
          role: "grid",
          "aria-rowcount": String(row_count),
          "aria-colcount": String(effectiveColumns.length),
        },
        React.createElement(
          "thead",
          { key: "sheet-thead" },
          React.createElement(
            "tr",
            {
              key: "col-letter-row",
              className: "f35-sheet-letter-row",
              "data-testid": "column-letter-row",
            },
            letterHeaderCells
          ),
          React.createElement(
            "tr",
            {
              key: "col-field-row",
              className: "f35-sheet-field-row",
              "data-testid": "column-field-row",
            },
            fieldHeaderCells
          )
        ),
        React.createElement(
          "tbody",
          { key: "sheet-tbody", "data-testid": "sheet-tbody" },
          bodyRows
        ),
        React.createElement(
          "tfoot",
          { key: "sheet-tfoot", "data-testid": "sheet-formula-footer" },
          React.createElement(
            "tr",
            {
              key: "formula-summary-row",
              className: "f35-sheet-footer-row",
              "data-testid": "formula-summary-row",
            },
            React.createElement(
              "td",
              {
                key: "footer-gutter",
                className: "f35-sheet-row-gutter",
                "data-testid": "footer-fx-label",
              },
              "∑ FX"
            ),
            React.createElement(
              "td",
              {
                key: "footer-formulas",
                className: "f35-sheet-cell",
                colSpan: footerColSpan,
              },
              ...footerFormulaSpans
            )
          )
        )
      )
    )
  );
};

export default MaintenanceSheetCard;
