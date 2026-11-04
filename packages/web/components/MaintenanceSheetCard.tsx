/**
 * @fileoverview UC0 F-35 ODIN/ALIS Maintenance Work Order Spreadsheet Card (`MaintenanceSheetCard.tsx`).
 *
 * Renders an Excel / Google Sheets-like interactive maintenance grid for
 * `@F35-Maintenance-Data` (`f35_maintenance_data_agent`) backed by
 * `antig-dave.ukd_f35_sustainment_demo.maintenance_work_orders` (BigQuery `EU`).
 *
 * Features:
 * - Top spreadsheet toolbar with sheet title, row/column count badge, EU BigQuery
 *   execution source & latency badge, and a clickable
 *   `[📥 Download .CSV (Excel / Google Sheets)]` anchor tag bound to `csv_download_url`.
 * - Formula bar (`fx`) displaying the executed read-only SQL query or active cell formula.
 * - Dual-row Excel/Google Sheets column header with column letters (`A`, `B`, `C`... `R`)
 *   above field display labels and semantic description tooltips (`title={col.description}`).
 * - Numbered row gutter (`1`, `2`, `3`...), colour-coded status pills for `aircraft_status`
 *   (`🟢 FMC`, `🟡 PMC-M`, `🟠 NMC-M`, `🔴 NMC-S (MICAP)`), and a sticky `∑ FX` formula
 *   summary footer row (`=COUNTA(...)`, `=SUM(logged_man_hours)`, `=AVERAGE(estimated_mttr_hours)`,
 *   `=COUNTIF(..., "NMC-S")`).
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
 * Column metadata for the Excel / Google Sheets-like Maintenance Card.
 * Mirrors `SpreadsheetColumnHeader` in `app/schemas.py`.
 */
export interface SpreadsheetColumnHeader {
  /** Excel/Sheets column letter (`A`..`R`). */
  col_letter: string;
  /** Underlying BigQuery column name (`work_order_id`, `tail_number`, etc.). */
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
  /** Execution source (`bigquery_eu_live` or deterministic EU seed fallback). */
  execution_source: string;
  /** Query execution and card serialization latency in milliseconds. */
  execution_latency_ms: number;
  /** Total number of work order rows returned. */
  row_count: number;
  /** Ordered column definitions with Excel letters (`A`..`R`) and semantic tooltips. */
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
}

/** Alias matching backend `MaintenanceSpreadsheetCard` model name. */
export type MaintenanceSpreadsheetCard = MaintenanceSpreadsheetCardProps;

/**
 * Authoritative mapping of F-35 ODIN/ALIS aircraft readiness codes to
 * colour-coded spreadsheet status badges.
 */
export const MAINTENANCE_STATUS_BADGES: Readonly<Record<string, string>> = Object.freeze({
  FMC: "🟢 FMC",
  "PMC-M": "🟡 PMC-M",
  "NMC-M": "🟠 NMC-M",
  "NMC-S": "🔴 NMC-S (MICAP)",
});

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
}
.f35-sheet-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
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
 * Formats an F-35 aircraft readiness status code into the canonical colour-coded
 * status badge required by UC0 (`f35_maintenance_data_agent`):
 * - `"FMC"` -> `"🟢 FMC"`
 * - `"PMC-M"` -> `"🟡 PMC-M"`
 * - `"NMC-M"` -> `"🟠 NMC-M"`
 * - `"NMC-S"` -> `"🔴 NMC-S (MICAP)"`
 */
export function formatStatusBadge(status: string): string {
  const normalized = String(status ?? "").trim();
  const upper = normalized.toUpperCase();

  if (upper === "FMC" || normalized === "🟢 FMC") {
    return "🟢 FMC";
  }
  if (upper === "PMC-M" || normalized === "🟡 PMC-M") {
    return "🟡 PMC-M";
  }
  if (upper === "NMC-M" || normalized === "🟠 NMC-M") {
    return "🟠 NMC-M";
  }
  if (
    upper === "NMC-S" ||
    upper === "NMC-S (MICAP)" ||
    normalized === "🔴 NMC-S (MICAP)" ||
    normalized === "🔴 NMC-S"
  ) {
    return "🔴 NMC-S (MICAP)";
  }
  return normalized || "⚪ UNKNOWN";
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
  if (fieldName === "aircraft_status") {
    const badge = formatStatusBadge(String(rawValue));
    return React.createElement(
      "span",
      {
        className: "f35-sheet-status-pill",
        "data-status-code": String(rawValue),
      },
      badge
    );
  }
  if (typeof rawValue === "boolean") {
    return rawValue ? "TRUE" : "FALSE";
  }
  if (
    typeof rawValue === "number" &&
    (fieldName === "logged_man_hours" || fieldName === "estimated_mttr_hours")
  ) {
    return rawValue.toFixed(1);
  }
  return String(rawValue);
}

/**
 * Interactive Excel / Google Sheets-like Maintenance Work Order Grid (`MaintenanceSheetCard`)
 * for UC0 (`@F35-Maintenance-Data`).
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

  const effectiveColumns: SpreadsheetColumnHeader[] =
    columns.length > 0
      ? columns.map((col, idx) => ({
          ...col,
          col_letter: col.col_letter || indexToColumnLetter(idx),
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
    const workOrderId = String(row.work_order_id ?? `ROW-${rowNumber}`);
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
        key: `row-${workOrderId}-${rowNumber}`,
        "data-row-index": String(rowNumber),
        "data-work-order-id": workOrderId,
      },
      cells
    );
  });

  const footerColSpan = Math.max(effectiveColumns.length, 1);

  return React.createElement(
    "section",
    {
      className: "f35-sheet-card",
      "data-component": "MaintenanceSheetCard",
      "data-sheet-id": sheet_id,
      "data-execution-source": execution_source,
      "data-csv-gcs-uri": csv_gcs_uri,
      "aria-label": `Maintenance Spreadsheet Card: ${sheet_title}`,
    },
    React.createElement("style", { key: "sheet-styles" }, MAINTENANCE_SHEET_CARD_STYLES),
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
      { key: "grid-scroll", className: "f35-sheet-grid-scroll" },
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
                },
                formula_footer.micap_count_formula
              )
            )
          )
        )
      )
    )
  );
};

export default MaintenanceSheetCard;
