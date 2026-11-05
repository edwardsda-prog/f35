"""UC0 Conversational Maintenance Log Explorer & Spreadsheet Card Tool (`f35_maintenance_data_agent`).

Executes validated read-only SELECT queries against BigQuery EU Table 7
(`antig-dave.ukd_f35_sustainment_demo.maintenance_work_orders`) with an instant
in-memory SQLite fallback, renders an interactive Excel / Google Sheets-like
Spreadsheet Card with Column Letters (A..R), Status Badges, Formula Summary Footer,
and automatically exports a downloadable .CSV to `gs://antig-dave-f35-staging-europe-west1/exports/`.
"""

from __future__ import annotations

import csv
import io
import json
import logging
import re
import sqlite3
import threading
import time
from typing import Any

from google.adk.tools.tool_context import ToolContext

from app.clients import _serialize_bq_val, get_bq_client, upload_csv_export
from app.config import BQ_LOCATION, BQ_TABLES, USE_CLOUD_CLIENTS
from app.schemas import (
    MaintenanceSpreadsheetCard,
    SpreadsheetColumnHeader,
    SpreadsheetFormulaFooter,
)
from app.seed_data.bq_seed_records import MAINTENANCE_WORK_ORDERS_ROWS, SCHEMAS_DIR

logger = logging.getLogger(__name__)

_TABLE_FQN = BQ_TABLES["maintenance_work_orders"]

_FORBIDDEN_SQL_KEYWORDS_RE = re.compile(
    r"\b(DROP|DELETE|UPDATE|INSERT|ALTER|TRUNCATE|CREATE|MERGE|GRANT|REVOKE|REPLACE|EXEC|EXECUTE|CALL)\b",
    re.IGNORECASE,
)
_SELECT_OR_WITH_START_RE = re.compile(r"^\s*(SELECT|WITH)\b", re.IGNORECASE)
_TABLE_REF_RE = re.compile(
    r"`?(?:antig-dave\.ukd_f35_sustainment_demo\.|ukd_f35_sustainment_demo\.)?maintenance_work_orders`?",
    re.IGNORECASE,
)
_NON_FILENAME_CHARS_RE = re.compile(r"[^A-Za-z0-9_.-]+")

_STATUS_BADGE_MAP: dict[str, str] = {
    "FMC": "🟢 FMC",
    "PMC-M": "🟡 PMC-M",
    "NMC-M": "🟠 NMC-M",
    "NMC-S": "🔴 NMC-S (MICAP)",
    "NMC-S (MICAP)": "🔴 NMC-S (MICAP)",
}

# Load column metadata from declarative JSON schema
_SCHEMA_FILE = SCHEMAS_DIR / "maintenance_work_orders.schema.json"
_COLUMN_META: dict[str, dict[str, str]] = {}
if _SCHEMA_FILE.exists():
    try:
        _spec = json.loads(_SCHEMA_FILE.read_text(encoding="utf-8"))
        for _field in _spec.get("fields", []):
            _COLUMN_META[_field["name"]] = {
                "type": _field.get("type", "STRING"),
                "description": _field.get("description", ""),
            }
    except Exception as _exc:  # pragma: no cover
        logger.warning("Failed loading maintenance_work_orders schema metadata: %s", _exc)

# Pre-populate in-memory SQLite engine at module import time for < 2 ms local SQL evaluation
_sqlite_lock = threading.Lock()
_sqlite_conn = sqlite3.connect(":memory:", check_same_thread=False)
_sqlite_conn.row_factory = sqlite3.Row


def _init_in_memory_sqlite() -> None:
    """Create and seed the in-memory SQLite maintenance_work_orders table at import time."""
    with _sqlite_lock:
        cur = _sqlite_conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS maintenance_work_orders (
                work_order_id TEXT PRIMARY KEY,
                tail_number TEXT NOT NULL,
                aircraft_variant TEXT NOT NULL,
                squadron TEXT NOT NULL,
                base_location TEXT NOT NULL,
                aircraft_status TEXT NOT NULL,
                work_order_status TEXT NOT NULL,
                priority TEXT NOT NULL,
                work_center TEXT NOT NULL,
                wuc_code TEXT NOT NULL,
                subsystem_name TEXT NOT NULL,
                discrepancy_narrative TEXT NOT NULL,
                corrective_action TEXT,
                awaiting_part_nsn TEXT,
                assigned_shift_lead TEXT NOT NULL,
                estimated_mttr_hours REAL NOT NULL,
                logged_man_hours REAL NOT NULL,
                created_at_utc TEXT NOT NULL
            )
            """
        )
        cur.execute("DELETE FROM maintenance_work_orders")
        for row in MAINTENANCE_WORK_ORDERS_ROWS:
            cur.execute(
                """
                INSERT INTO maintenance_work_orders (
                    work_order_id, tail_number, aircraft_variant, squadron,
                    base_location, aircraft_status, work_order_status, priority,
                    work_center, wuc_code, subsystem_name, discrepancy_narrative,
                    corrective_action, awaiting_part_nsn, assigned_shift_lead,
                    estimated_mttr_hours, logged_man_hours, created_at_utc
                ) VALUES (
                    :work_order_id, :tail_number, :aircraft_variant, :squadron,
                    :base_location, :aircraft_status, :work_order_status, :priority,
                    :work_center, :wuc_code, :subsystem_name, :discrepancy_narrative,
                    :corrective_action, :awaiting_part_nsn, :assigned_shift_lead,
                    :estimated_mttr_hours, :logged_man_hours, :created_at_utc
                )
                """,
                row,
            )
        _sqlite_conn.commit()


_init_in_memory_sqlite()


def _index_to_column_letter(idx: int) -> str:
    """Convert 0-based column index to Excel / Google Sheets column letter (A..Z, AA..ZZ)."""
    result = ""
    n = idx + 1
    while n > 0:
        n, rem = divmod(n - 1, 26)
        result = chr(65 + rem) + result
    return result


def validate_and_rewrite_maintenance_sql(sql_query: str) -> tuple[str, str]:
    """Validate that sql_query is a safe read-only SELECT on maintenance_work_orders.

    Returns:
        Tuple of (bq_qualified_sql, sqlite_compatible_sql).

    Raises:
        ValueError: If sql_query is empty, non-SELECT, contains DML/DDL keywords,
            contains multiple semicolon-delimited statements, or does not reference
            `maintenance_work_orders`.
    """
    if not sql_query or not sql_query.strip():
        raise ValueError("SQL query cannot be empty.")

    # Strip SQL comments and trailing semicolons
    cleaned = re.sub(r"--[^\n]*", " ", sql_query)
    cleaned = re.sub(r"/\*.*?\*/", " ", cleaned, flags=re.DOTALL).strip()
    if cleaned.endswith(";"):
        cleaned = cleaned[:-1].strip()

    if ";" in cleaned:
        raise ValueError(
            "Unsafe SQL rejected: multiple semicolon-separated SQL statements are not permitted."
        )

    if not _SELECT_OR_WITH_START_RE.match(cleaned):
        raise ValueError(
            "Unsafe SQL rejected: only read-only SELECT (or WITH ... SELECT) queries are permitted."
        )

    forbidden_match = _FORBIDDEN_SQL_KEYWORDS_RE.search(cleaned)
    if forbidden_match:
        keyword = forbidden_match.group(1).upper()
        raise ValueError(
            f"Unsafe SQL rejected: forbidden DML/DDL keyword '{keyword}' detected."
        )

    if not _TABLE_REF_RE.search(cleaned):
        raise ValueError(
            "Invalid SQL target: query must reference `maintenance_work_orders`."
        )

    bq_sql = _TABLE_REF_RE.sub(f"`{_TABLE_FQN}`", cleaned)
    sqlite_sql = _TABLE_REF_RE.sub("maintenance_work_orders", cleaned)
    # Translate BigQuery COUNTIF(cond) -> SUM(CASE WHEN cond THEN 1 ELSE 0 END) for SQLite compatibility
    sqlite_sql = re.sub(
        r"\bCOUNTIF\s*\(([^)]+)\)",
        r"SUM(CASE WHEN \1 THEN 1 ELSE 0 END)",
        sqlite_sql,
        flags=re.IGNORECASE,
    )
    return bq_sql, sqlite_sql


def _execute_sqlite_fallback(sqlite_sql: str) -> list[dict[str, Any]]:
    """Execute validated SELECT query against the pre-populated in-memory SQLite table."""
    with _sqlite_lock:
        cur = _sqlite_conn.cursor()
        cur.execute(sqlite_sql)
        col_names = [desc[0] for desc in (cur.description or [])]
        return [dict(zip(col_names, row)) for row in cur.fetchall()]


def _format_status_badge(val: Any) -> str:
    """Format aircraft_status values with visual readiness status badges."""
    if val is None:
        return "—"
    raw = str(val).strip()
    return _STATUS_BADGE_MAP.get(raw.upper(), raw)


def _build_csv_string(field_names: list[str], rows: list[dict[str, Any]]) -> str:
    """Serialize query result rows to an RFC-4180 UTF-8 CSV string."""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=field_names, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow({k: ("" if row.get(k) is None else row.get(k)) for k in field_names})
    return buf.getvalue()


def execute_maintenance_sql(
    sql_query: str,
    sheet_title: str = "F35_ODIN_Maintenance_Work_Orders",
    tool_context: ToolContext | None = None,
) -> dict[str, Any]:
    """Execute Maintenance Work Order SQL & Render Spreadsheet Card.

    Validates and runs a read-only SELECT query against BigQuery EU Table 7
    (`antig-dave.ukd_f35_sustainment_demo.maintenance_work_orders`), formats an
    Excel / Google Sheets-like Spreadsheet Card with Column Letters (A..R),
    readiness status badges, and formula summary footers, and exports the result
    as a downloadable CSV in `gs://antig-dave-f35-staging-europe-west1/exports/`.

    Args:
        sql_query: Read-only SELECT SQL query over `maintenance_work_orders`.
        sheet_title: Descriptive title for the spreadsheet card and exported CSV filename.
        tool_context: Optional ADK ToolContext for persisting the latest spreadsheet card in session state.

    Returns:
        Dictionary containing `spreadsheet_card_markdown`, `spreadsheet_card`, `rows`,
        `columns`, `formula_footer`, `csv_download_url`, `csv_gcs_uri`, and execution metadata.
    """
    t0 = time.perf_counter()
    bq_sql, sqlite_sql = validate_and_rewrite_maintenance_sql(sql_query)

    rows: list[dict[str, Any]] = []
    execution_source = "BIGQUERY_EU"

    if USE_CLOUD_CLIENTS:
        try:
            from google.cloud import bigquery

            client = get_bq_client()
            job_config = bigquery.QueryJobConfig(use_query_cache=True)
            if hasattr(client, "query_and_wait"):
                row_iter = client.query_and_wait(
                    bq_sql,
                    job_config=job_config,
                    location=BQ_LOCATION,
                )
            else:
                row_iter = client.query(
                    bq_sql,
                    job_config=job_config,
                    location=BQ_LOCATION,
                ).result()
            rows = [
                {k: _serialize_bq_val(v) for k, v in dict(row.items()).items()}
                for row in row_iter
            ]
        except Exception as exc:
            logger.warning(
                "BigQuery EU query fallback to in-memory SQLite for maintenance_work_orders: %s",
                exc,
            )
            rows = _execute_sqlite_fallback(sqlite_sql)
            execution_source = "SQLITE_IN_MEMORY_FALLBACK"
    else:
        rows = _execute_sqlite_fallback(sqlite_sql)
        execution_source = "SQLITE_IN_MEMORY_FALLBACK"

    latency_ms = round((time.perf_counter() - t0) * 1000.0, 2)

    if rows:
        field_names = list(rows[0].keys())
    else:
        field_names = list(_COLUMN_META.keys()) or [
            "work_order_id",
            "tail_number",
            "aircraft_status",
            "work_order_status",
            "priority",
            "wuc_code",
            "subsystem_name",
            "estimated_mttr_hours",
            "logged_man_hours",
        ]

    columns: list[SpreadsheetColumnHeader] = []
    for idx, fname in enumerate(field_names):
        col_letter = _index_to_column_letter(idx)
        meta = _COLUMN_META.get(fname, {})
        columns.append(
            SpreadsheetColumnHeader(
                column_letter=col_letter,
                col_letter=col_letter,
                field_name=fname,
                display_label=f"{col_letter}: {fname}",
                data_type=meta.get("type", "STRING"),
                description=meta.get("description", f"Query column {fname}"),
            )
        )

    # Compute formula summary footer metrics
    total_rows = len(rows)
    end_row_num = max(2, total_rows + 1)

    logged_hours_vals = [
        float(r["logged_man_hours"])
        for r in rows
        if r.get("logged_man_hours") is not None
        and isinstance(r.get("logged_man_hours"), (int, float))
    ]
    mttr_vals = [
        float(r["estimated_mttr_hours"])
        for r in rows
        if r.get("estimated_mttr_hours") is not None
        and isinstance(r.get("estimated_mttr_hours"), (int, float))
    ]
    # Also support aggregated alias columns if query used SUM/AVG
    if not logged_hours_vals:
        for r in rows:
            for k, v in r.items():
                if "logged" in k.lower() and isinstance(v, (int, float)):
                    logged_hours_vals.append(float(v))
    if not mttr_vals:
        for r in rows:
            for k, v in r.items():
                if "mttr" in k.lower() and isinstance(v, (int, float)):
                    mttr_vals.append(float(v))

    sum_logged = round(sum(logged_hours_vals), 2) if logged_hours_vals else 0.0
    avg_mttr = round(sum(mttr_vals) / len(mttr_vals), 2) if mttr_vals else 0.0
    micap_cnt = sum(
        1
        for r in rows
        if str(r.get("aircraft_status", "")).upper().startswith("NMC-S")
        or "MICAP" in str(r.get("work_order_status", "")).upper()
    )

    footer = SpreadsheetFormulaFooter(
        row_count_formula=f"=COUNTA(A2:A{end_row_num})",
        total_rows=total_rows,
        sum_logged_man_hours_formula=f"=SUM(logged_man_hours) -> {sum_logged:.1f} hrs",
        total_man_hours_formula=f"=SUM(logged_man_hours) -> {sum_logged:.1f} hrs",
        sum_logged_man_hours=sum_logged,
        avg_estimated_mttr_hours_formula=f"=AVERAGE(estimated_mttr_hours) -> {avg_mttr:.2f} hrs",
        avg_mttr_hours_formula=f"=AVERAGE(estimated_mttr_hours) -> {avg_mttr:.2f} hrs",
        avg_estimated_mttr_hours=avg_mttr,
        micap_count_formula=f'=COUNTIF(aircraft_status, "NMC-S") -> {micap_cnt} MICAP',
    )

    # Export CSV to GCS europe-west1
    clean_title = _NON_FILENAME_CHARS_RE.sub("_", sheet_title.strip()) or "F35_ODIN_Maintenance_Work_Orders"
    if clean_title.lower().endswith(".csv"):
        clean_title = clean_title[:-4]
    csv_filename = f"{clean_title}.csv"
    csv_content = _build_csv_string(field_names, rows)
    export_info = upload_csv_export(csv_content=csv_content, filename=csv_filename)

    # Build Markdown Spreadsheet Card
    header_cells = ["#"] + [f"**{c.column_letter}** `{c.field_name}`" for c in columns]
    align_cells = ["---:"] + [
        "---:" if c.data_type in ("FLOAT", "FLOAT64", "INT64", "INTEGER", "NUMERIC") else ":---"
        for c in columns
    ]

    has_logged_col = any("logged" in c.field_name.lower() for c in columns)
    has_mttr_col = any("mttr" in c.field_name.lower() for c in columns)

    md_lines: list[str] = [
        f"### 📊 Spreadsheet Card: `{clean_title}`",
        (
            f"**Repository:** F35 Datawarehouse (`maintenance_work_orders`) · "
            f"**Rows:** `{total_rows}` · **Columns:** `{len(columns)}` (`A`–`{columns[-1].column_letter if columns else 'A'}`) · "
            f"**Latency:** `{latency_ms} ms`"
        ),
        "",
        "| " + " | ".join(header_cells) + " |",
        "| " + " | ".join(align_cells) + " |",
    ]

    for row_idx, row in enumerate(rows, start=2):
        row_cells = [f"`{row_idx}`"]
        for col in columns:
            val = row.get(col.field_name)
            if col.field_name == "aircraft_status":
                cell_str = _format_status_badge(val)
            elif val is None:
                cell_str = "`NULL`"
            elif isinstance(val, float):
                cell_str = f"{val:.2f}".rstrip("0").rstrip(".") if "." in f"{val:.2f}" else str(val)
            else:
                cell_str = str(val).replace("|", "\\|").replace("\n", " ")
            row_cells.append(cell_str)
        md_lines.append("| " + " | ".join(row_cells) + " |")

    # Append Formula Summary Footer Row in Markdown table
    footer_cells = ["**`fx`**"]
    for idx, col in enumerate(columns):
        fname_lower = col.field_name.lower()
        if idx == 0:
            footer_cells.append(f"**`{footer.row_count_formula}` → `{footer.total_rows} rows`**")
        elif ("logged" in fname_lower) and sum_logged > 0:
            footer_cells.append(
                f"**`{footer.sum_logged_man_hours_formula}` = `{footer.sum_logged_man_hours:.1f} hrs`**"
            )
        elif ("mttr" in fname_lower) and avg_mttr > 0:
            footer_cells.append(
                f"**`{footer.avg_estimated_mttr_hours_formula}` = `{footer.avg_estimated_mttr_hours:.2f} hrs`**"
            )
        else:
            footer_cells.append("—")
    md_lines.append("| " + " | ".join(footer_cells) + " |")

    # Build Formula Summary Bar items
    summary_bar_items = [f"`{footer.row_count_formula} = {footer.total_rows}`"]
    if has_logged_col and sum_logged > 0:
        summary_bar_items.append(f"`{footer.sum_logged_man_hours_formula} = {footer.sum_logged_man_hours:.1f} hrs`")
    if has_mttr_col and avg_mttr > 0:
        summary_bar_items.append(f"`{footer.avg_estimated_mttr_hours_formula} = {footer.avg_estimated_mttr_hours:.2f} hrs`")

    md_lines.extend(
        [
            "",
            f"**Formula Summary Bar:** " + " · ".join(summary_bar_items),
            "",
            "<details><summary>🔍 View Executed Query</summary>",
            "",
            "```sql",
            bq_sql,
            "```",
            "</details>",
        ]
    )

    card_markdown = "\n".join(md_lines)

    card = MaintenanceSpreadsheetCard(
        sheet_id=clean_title,
        sheet_title=clean_title,
        table_fqn=_TABLE_FQN,
        bq_location=BQ_LOCATION,
        executed_sql=bq_sql,
        execution_source=execution_source,
        execution_latency_ms=latency_ms,
        row_count=total_rows,
        column_count=len(columns),
        columns=columns,
        rows=rows,
        formula_footer=footer,
        csv_gcs_uri=export_info["gcs_uri"],
        csv_download_url=export_info["download_url"],
        spreadsheet_card_markdown=card_markdown,
    )

    if tool_context is not None:
        state = getattr(tool_context, "state", None)
        if isinstance(state, dict):
            state["last_uc0_spreadsheet_card"] = card.model_dump()

    return {
        "status": "SUCCESS",
        "sheet_title": clean_title,
        "table_fqn": _TABLE_FQN,
        "bq_location": BQ_LOCATION,
        "executed_sql": bq_sql,
        "execution_source": execution_source,
        "execution_latency_ms": latency_ms,
        "row_count": total_rows,
        "column_count": len(columns),
        "columns": [c.model_dump() for c in columns],
        "rows": rows,
        "formula_footer": footer.model_dump(),
        "csv_gcs_uri": export_info["gcs_uri"],
        "csv_download_url": export_info["download_url"],
        "spreadsheet_card": card.model_dump(),
        "spreadsheet_card_markdown": card_markdown,
    }


__all__ = [
    "execute_maintenance_sql",
    "validate_and_rewrite_maintenance_sql",
]
