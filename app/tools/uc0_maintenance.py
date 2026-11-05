"""UC0 / UC0.1 / UC0.5 Conversational Maintenance, PHM/BIT & SQEP Tooling Explorer (`f35_maintenance_data_agent`).

Executes validated read-only SELECT and JOIN queries against BigQuery EU Tables 7, 8, and 9:
- Table 7: `antig-dave.ukd_f35_sustainment_demo.maintenance_work_orders`
- Table 8: `antig-dave.ukd_f35_sustainment_demo.phm_bit_fault_events` (UC 0.1)
- Table 9: `antig-dave.ukd_f35_sustainment_demo.work_center_tooling_and_sqep` (UC 0.5)
with an instant in-memory SQLite fallback (100 rows per table = 300 rows), renders an
interactive Excel / Google Sheets-like Spreadsheet Card with Column Letters (A..Z),
Status Badges, Formula Summary Footer, and automatically exports a downloadable .CSV
to `gs://antig-dave-f35-staging-europe-west1/exports/`.
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
from app.config import BQ_DATASET_FQN, BQ_LOCATION, BQ_TABLES, USE_CLOUD_CLIENTS
from app.schemas import (
    MaintenanceSpreadsheetCard,
    SpreadsheetColumnHeader,
    SpreadsheetFormulaFooter,
)
from app.seed_data.bq_seed_records import (
    MAINTENANCE_WORK_ORDERS_ROWS,
    PHM_BIT_FAULT_EVENTS_ROWS,
    SCHEMAS_DIR,
    WORK_CENTER_TOOLING_AND_SQEP_ROWS,
)

logger = logging.getLogger(__name__)

_TABLE_FQN = BQ_TABLES["maintenance_work_orders"]
_ALLOWED_UC0_TABLES: tuple[str, ...] = (
    "maintenance_work_orders",
    "phm_bit_fault_events",
    "work_center_tooling_and_sqep",
)

_FORBIDDEN_SQL_KEYWORDS_RE = re.compile(
    r"\b(DROP|DELETE|UPDATE|INSERT|ALTER|TRUNCATE|CREATE|MERGE|GRANT|REVOKE|REPLACE|EXEC|EXECUTE|CALL)\b",
    re.IGNORECASE,
)
_SELECT_OR_WITH_START_RE = re.compile(r"^\s*(SELECT|WITH)\b", re.IGNORECASE)
_TABLE_REF_RE = re.compile(
    r"`?(?:antig-dave\.ukd_f35_sustainment_demo\.|ukd_f35_sustainment_demo\.)?"
    r"\b(maintenance_work_orders|phm_bit_fault_events|work_center_tooling_and_sqep)\b`?",
    re.IGNORECASE,
)
_NON_FILENAME_CHARS_RE = re.compile(r"[^A-Za-z0-9_.-]+")

_MAX_MARKDOWN_PREVIEW_ROWS = 25

_STATUS_BADGE_MAP: dict[str, str] = {
    "FMC": "🟢 FMC",
    "PMC-M": "🟡 PMC-M",
    "NMC-M": "🟠 NMC-M",
    "NMC-S": "🔴 NMC-S (MICAP)",
    "NMC-S (MICAP)": "🔴 NMC-S (MICAP)",
}

_FAULT_SEVERITY_BADGE_MAP: dict[str, str] = {
    "CRITICAL_GROUNDING": "🔴 CRITICAL_GROUNDING",
    "DEGRADED_PMC": "🟠 DEGRADED_PMC",
    "ADVISORY_PHM": "🟡 ADVISORY_PHM",
    "NO_BIT_FAULT_LOGGED": "⚪ NO_BIT_FAULT_LOGGED",
}

_TOOL_CAL_BADGE_MAP: dict[str, str] = {
    "CALIBRATED_SERVICEABLE": "🟢 CALIBRATED_SERVICEABLE",
    "CALIBRATION_DUE_WARNING": "🟡 CALIBRATION_DUE_WARNING",
    "EXPIRED_OUT_OF_CAL": "🔴 EXPIRED_OUT_OF_CAL",
    "IN_USE_OTHER_BAY": "🟠 IN_USE_OTHER_BAY",
}

_BAY_DISPATCH_BADGE_MAP: dict[str, str] = {
    "READY_TO_DISPATCH": "🟢 READY_TO_DISPATCH",
    "BLOCKED_TOOL_OUT_OF_CAL": "🔴 BLOCKED_TOOL_OUT_OF_CAL",
    "BLOCKED_NO_QAR_ON_SHIFT": "🟠 BLOCKED_NO_QAR_ON_SHIFT",
    "BLOCKED_AWAITING_MICAP_PART": "🔴 BLOCKED_AWAITING_MICAP_PART",
}

_BOOLEAN_COLUMNS: frozenset[str] = frozenset({"cnd_flag", "qar_inspector_available"})

# Load column metadata from all 3 declarative JSON schemas (Tables 7, 8, and 9)
_COLUMN_META: dict[str, dict[str, str]] = {}
for _schema_fname in (
    "maintenance_work_orders.schema.json",
    "phm_bit_fault_events.schema.json",
    "work_center_tooling_and_sqep.schema.json",
):
    _schema_file = SCHEMAS_DIR / _schema_fname
    if _schema_file.exists():
        try:
            _spec = json.loads(_schema_file.read_text(encoding="utf-8"))
            for _field in _spec.get("fields", []):
                _COLUMN_META.setdefault(
                    _field["name"],
                    {
                        "type": _field.get("type", "STRING"),
                        "description": _field.get("description", ""),
                    },
                )
        except Exception as _exc:  # pragma: no cover
            logger.warning("Failed loading %s metadata: %s", _schema_fname, _exc)

# Pre-populate in-memory SQLite engine at module import time for < 2 ms local SQL evaluation
_sqlite_lock = threading.Lock()
_sqlite_conn = sqlite3.connect(":memory:", check_same_thread=False)
_sqlite_conn.row_factory = sqlite3.Row


def _init_in_memory_sqlite() -> None:
    """Create and seed the in-memory SQLite Tables 7, 8, and 9 (100 rows each) at import time."""
    with _sqlite_lock:
        cur = _sqlite_conn.cursor()
        # Table 7: maintenance_work_orders
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

        # Table 8: phm_bit_fault_events (UC 0.1)
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS phm_bit_fault_events (
                fault_event_id TEXT PRIMARY KEY,
                tail_number TEXT NOT NULL,
                aircraft_variant TEXT NOT NULL,
                squadron TEXT NOT NULL,
                base_location TEXT NOT NULL,
                sortie_id TEXT,
                wuc_code TEXT NOT NULL,
                subsystem_name TEXT NOT NULL,
                hrc_code TEXT NOT NULL,
                fault_severity TEXT NOT NULL,
                bit_trigger_type TEXT NOT NULL,
                recurrence_count_30d INTEGER NOT NULL,
                cnd_flag BOOLEAN NOT NULL,
                diagnostic_confidence_pct REAL NOT NULL,
                linked_work_order_id TEXT,
                fault_timestamp_utc TEXT NOT NULL
            )
            """
        )
        cur.execute("DELETE FROM phm_bit_fault_events")
        for row in PHM_BIT_FAULT_EVENTS_ROWS:
            cur.execute(
                """
                INSERT INTO phm_bit_fault_events (
                    fault_event_id, tail_number, aircraft_variant, squadron,
                    base_location, sortie_id, wuc_code, subsystem_name,
                    hrc_code, fault_severity, bit_trigger_type, recurrence_count_30d,
                    cnd_flag, diagnostic_confidence_pct, linked_work_order_id,
                    fault_timestamp_utc
                ) VALUES (
                    :fault_event_id, :tail_number, :aircraft_variant, :squadron,
                    :base_location, :sortie_id, :wuc_code, :subsystem_name,
                    :hrc_code, :fault_severity, :bit_trigger_type, :recurrence_count_30d,
                    :cnd_flag, :diagnostic_confidence_pct, :linked_work_order_id,
                    :fault_timestamp_utc
                )
                """,
                row,
            )

        # Table 9: work_center_tooling_and_sqep (UC 0.5)
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS work_center_tooling_and_sqep (
                resource_id TEXT PRIMARY KEY,
                assigned_work_order_id TEXT,
                base_location TEXT NOT NULL,
                work_center TEXT NOT NULL,
                supported_wuc_code TEXT NOT NULL,
                shift_code TEXT NOT NULL,
                shift_lead_name TEXT NOT NULL,
                sqep_certification_domain TEXT NOT NULL,
                sqep_certified_techs_on_shift INTEGER NOT NULL,
                qar_inspector_available BOOLEAN NOT NULL,
                required_special_tool_id TEXT NOT NULL,
                required_special_tool_name TEXT NOT NULL,
                tool_calibration_status TEXT NOT NULL,
                calibration_expiry_utc TEXT NOT NULL,
                bay_dispatch_status TEXT NOT NULL,
                shift_updated_utc TEXT NOT NULL
            )
            """
        )
        cur.execute("DELETE FROM work_center_tooling_and_sqep")
        for row in WORK_CENTER_TOOLING_AND_SQEP_ROWS:
            cur.execute(
                """
                INSERT INTO work_center_tooling_and_sqep (
                    resource_id, assigned_work_order_id, base_location, work_center,
                    supported_wuc_code, shift_code, shift_lead_name, sqep_certification_domain,
                    sqep_certified_techs_on_shift, qar_inspector_available,
                    required_special_tool_id, required_special_tool_name,
                    tool_calibration_status, calibration_expiry_utc,
                    bay_dispatch_status, shift_updated_utc
                ) VALUES (
                    :resource_id, :assigned_work_order_id, :base_location, :work_center,
                    :supported_wuc_code, :shift_code, :shift_lead_name, :sqep_certification_domain,
                    :sqep_certified_techs_on_shift, :qar_inspector_available,
                    :required_special_tool_id, :required_special_tool_name,
                    :tool_calibration_status, :calibration_expiry_utc,
                    :bay_dispatch_status, :shift_updated_utc
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
    """Validate that sql_query is a safe read-only SELECT on UC0/UC0.1/UC0.5 tables.

    Supports single-table and multi-table JOIN queries referencing any combination of:
    - `maintenance_work_orders`
    - `phm_bit_fault_events`
    - `work_center_tooling_and_sqep`

    Returns:
        Tuple of (bq_qualified_sql, sqlite_compatible_sql).

    Raises:
        ValueError: If sql_query is empty, non-SELECT, contains DML/DDL keywords,
            contains multiple semicolon-delimited statements, or does not reference
            at least one of the allowed UC0 maintenance tables.
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
            "Invalid SQL target: query must reference at least one of "
            "`maintenance_work_orders`, `phm_bit_fault_events`, or `work_center_tooling_and_sqep`."
        )

    def _replace_bq(match: re.Match[str]) -> str:
        tbl_name = match.group(1).lower()
        end_pos = match.end()
        # If immediately followed by '.column_name', keep table identifier as-is for column qualification
        if end_pos < len(cleaned) and cleaned[end_pos] == ".":
            return tbl_name
        return f"`{BQ_DATASET_FQN}.{tbl_name}`"

    def _replace_sqlite(match: re.Match[str]) -> str:
        return match.group(1).lower()

    bq_sql = _TABLE_REF_RE.sub(_replace_bq, cleaned)
    sqlite_sql = _TABLE_REF_RE.sub(_replace_sqlite, cleaned)
    # Translate BigQuery COUNTIF(cond) -> SUM(CASE WHEN cond THEN 1 ELSE 0 END) for SQLite compatibility
    sqlite_sql = re.sub(
        r"\bCOUNTIF\s*\(([^)]+)\)",
        r"SUM(CASE WHEN \1 THEN 1 ELSE 0 END)",
        sqlite_sql,
        flags=re.IGNORECASE,
    )
    return bq_sql, sqlite_sql


def _execute_sqlite_fallback(sqlite_sql: str) -> list[dict[str, Any]]:
    """Execute validated SELECT/JOIN query against the pre-populated in-memory SQLite tables."""
    with _sqlite_lock:
        cur = _sqlite_conn.cursor()
        cur.execute(sqlite_sql)
        col_names = [desc[0] for desc in (cur.description or [])]
        result_rows: list[dict[str, Any]] = []
        for raw_row in cur.fetchall():
            row_dict = dict(zip(col_names, raw_row))
            for bcol in _BOOLEAN_COLUMNS:
                if bcol in row_dict and row_dict[bcol] in (0, 1):
                    row_dict[bcol] = bool(row_dict[bcol])
            result_rows.append(row_dict)
        return result_rows


def _format_cell_badge(field_name: str, val: Any) -> str | None:
    """Format status, severity, CND, calibration, and dispatch columns with visual badges."""
    if val is None:
        return None
    fname = field_name.lower()
    raw = str(val).strip()
    raw_upper = raw.upper()

    if fname == "aircraft_status":
        return _STATUS_BADGE_MAP.get(raw_upper, raw)
    if fname == "fault_severity":
        return _FAULT_SEVERITY_BADGE_MAP.get(raw_upper, raw)
    if fname == "cnd_flag":
        is_cnd = val is True or val == 1 or raw_upper in ("TRUE", "1", "YES")
        return "⚠️ CND (Repeat)" if is_cnd else "✅ Verified"
    if fname == "tool_calibration_status":
        return _TOOL_CAL_BADGE_MAP.get(raw_upper, raw)
    if fname == "bay_dispatch_status":
        return _BAY_DISPATCH_BADGE_MAP.get(raw_upper, raw)
    return None


def _build_csv_string(field_names: list[str], rows: list[dict[str, Any]]) -> str:
    """Serialize query result rows to an RFC-4180 UTF-8 CSV string."""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=field_names, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow({k: ("" if row.get(k) is None else row.get(k)) for k in field_names})
    return buf.getvalue()


def _resolve_numeric_series(
    rows: list[dict[str, Any]],
    candidates: tuple[tuple[str, str, str], ...],
    default_col: str,
    default_unit: str,
) -> tuple[str, str, list[float]]:
    """Select the first matching numeric column from candidates and extract its float values."""
    if not rows:
        return default_col, default_unit, []

    row_keys = list(rows[0].keys())
    for exact_col, substr_key, unit in candidates:
        matched_key = None
        if exact_col in row_keys:
            matched_key = exact_col
        else:
            for k in row_keys:
                if substr_key in k.lower() and k.lower() not in _BOOLEAN_COLUMNS:
                    matched_key = k
                    break
        if matched_key is not None:
            vals = [
                float(r[matched_key])
                for r in rows
                if r.get(matched_key) is not None
                and isinstance(r.get(matched_key), (int, float))
                and not isinstance(r.get(matched_key), bool)
            ]
            if vals:
                return matched_key, unit, vals

    # Fallback to any numeric column present in rows
    for k in row_keys:
        if k.lower() in _BOOLEAN_COLUMNS:
            continue
        vals = [
            float(r[k])
            for r in rows
            if r.get(k) is not None
            and isinstance(r.get(k), (int, float))
            and not isinstance(r.get(k), bool)
        ]
        if vals:
            return k, "", vals

    return default_col, default_unit, []


def execute_maintenance_sql(
    sql_query: str,
    sheet_title: str = "F35_ODIN_Maintenance_Work_Orders",
    tool_context: ToolContext | None = None,
) -> dict[str, Any]:
    """Execute Maintenance Work Order, PHM/BIT Fault, or SQEP/Tooling SQL & Render Spreadsheet Card.

    Validates and runs a read-only SELECT (including multi-table JOINs) against BigQuery EU:
    - Table 7: `antig-dave.ukd_f35_sustainment_demo.maintenance_work_orders` (UC 0)
    - Table 8: `antig-dave.ukd_f35_sustainment_demo.phm_bit_fault_events` (UC 0.1)
    - Table 9: `antig-dave.ukd_f35_sustainment_demo.work_center_tooling_and_sqep` (UC 0.5)
    Formats an Excel / Google Sheets-like Spreadsheet Card with Column Letters (A..Z),
    status/severity/calibration/dispatch badges, and formula summary footers, and exports
    the full result as a downloadable CSV in `gs://antig-dave-f35-staging-europe-west1/exports/`.

    Args:
        sql_query: Read-only SELECT / JOIN SQL query over `maintenance_work_orders`,
            `phm_bit_fault_events`, and/or `work_center_tooling_and_sqep`.
        sheet_title: Descriptive title for the spreadsheet card and exported CSV filename.
        tool_context: Optional ADK ToolContext for persisting the latest spreadsheet card in session state.

    Returns:
        Dictionary containing `spreadsheet_card_markdown`, `spreadsheet_card`, `rows`,
        `columns`, `formula_footer`, `csv_download_url`, `csv_gcs_uri`, and execution metadata.
    """
    t0 = time.perf_counter()
    bq_sql, sqlite_sql = validate_and_rewrite_maintenance_sql(sql_query)

    referenced_tables: list[str] = []
    for m in _TABLE_REF_RE.finditer(sql_query):
        tname = m.group(1).lower()
        if tname not in referenced_tables:
            referenced_tables.append(tname)
    primary_table = referenced_tables[0] if referenced_tables else "maintenance_work_orders"
    resolved_table_fqn = BQ_TABLES.get(primary_table, _TABLE_FQN)
    repo_tables_label = ", ".join(f"`{t}`" for t in referenced_tables) or "`maintenance_work_orders`"

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
                "BigQuery EU query fallback to in-memory SQLite for %s: %s",
                primary_table,
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
        field_names = [
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

    # Compute formula summary footer metrics dynamically across UC0, UC0.1, and UC0.5 columns
    total_rows = len(rows)
    end_row_num = max(2, total_rows + 1)

    sum_col, sum_unit, sum_vals = _resolve_numeric_series(
        rows,
        candidates=(
            ("logged_man_hours", "logged", "hrs"),
            ("recurrence_count_30d", "recurrence", "events"),
            ("sqep_certified_techs_on_shift", "sqep", "techs"),
            ("estimated_mttr_hours", "mttr", "hrs"),
        ),
        default_col="logged_man_hours",
        default_unit="hrs",
    )
    avg_col, avg_unit, avg_vals = _resolve_numeric_series(
        rows,
        candidates=(
            ("estimated_mttr_hours", "mttr", "hrs"),
            ("diagnostic_confidence_pct", "confidence", "%"),
            ("sqep_certified_techs_on_shift", "sqep", "techs"),
            ("recurrence_count_30d", "recurrence", "events"),
            ("logged_man_hours", "logged", "hrs"),
        ),
        default_col="estimated_mttr_hours",
        default_unit="hrs",
    )

    sum_logged = round(sum(sum_vals), 2) if sum_vals else 0.0
    avg_mttr = round(sum(avg_vals) / len(avg_vals), 2) if avg_vals else 0.0
    micap_cnt = sum(
        1
        for r in rows
        if str(r.get("aircraft_status", "")).upper().startswith("NMC-S")
        or "MICAP" in str(r.get("work_order_status", "")).upper()
        or "CRITICAL" in str(r.get("fault_severity", "")).upper()
        or "BLOCKED" in str(r.get("bay_dispatch_status", "")).upper()
    )

    sum_unit_suffix = f" {sum_unit}".rstrip()
    avg_unit_suffix = f" {avg_unit}".rstrip()

    footer = SpreadsheetFormulaFooter(
        row_count_formula=f"=COUNTA(A2:A{end_row_num})",
        total_rows=total_rows,
        sum_logged_man_hours_formula=f"=SUM({sum_col}) -> {sum_logged:.1f}{sum_unit_suffix}",
        total_man_hours_formula=f"=SUM({sum_col}) -> {sum_logged:.1f}{sum_unit_suffix}",
        sum_logged_man_hours=sum_logged,
        avg_estimated_mttr_hours_formula=f"=AVERAGE({avg_col}) -> {avg_mttr:.2f}{avg_unit_suffix}",
        avg_mttr_hours_formula=f"=AVERAGE({avg_col}) -> {avg_mttr:.2f}{avg_unit_suffix}",
        avg_estimated_mttr_hours=avg_mttr,
        micap_count_formula=f'=COUNTIF(status, "ALERT/MICAP") -> {micap_cnt}',
    )

    # Export full CSV to GCS europe-west1
    clean_title = (
        _NON_FILENAME_CHARS_RE.sub("_", sheet_title.strip())
        or "F35_ODIN_Maintenance_Work_Orders"
    )
    if clean_title.lower().endswith(".csv"):
        clean_title = clean_title[:-4]
    csv_filename = f"{clean_title}.csv"
    csv_content = _build_csv_string(field_names, rows)
    export_info = upload_csv_export(csv_content=csv_content, filename=csv_filename)

    # Build Markdown Spreadsheet Card (preview capped at 25 rows when total_rows > 25)
    header_cells = ["#"] + [f"**{c.column_letter}** · `{c.field_name}`" for c in columns]
    align_cells = ["---:"] + [
        "---:"
        if c.data_type in ("FLOAT", "FLOAT64", "INT64", "INTEGER", "NUMERIC")
        else ":---"
        for c in columns
    ]

    md_lines: list[str] = [
        f"### 📊 Spreadsheet Card: `{clean_title}`",
        (
            f"**Repository:** F35 Datawarehouse ({repo_tables_label}) · "
            f"**Rows:** `{total_rows}` · **Columns:** `{len(columns)}` (`A`–`{columns[-1].column_letter if columns else 'A'}`) · "
            f"**Latency:** `{latency_ms} ms`"
        ),
        "",
        "| " + " | ".join(header_cells) + " |",
        "| " + " | ".join(align_cells) + " |",
    ]

    preview_rows = rows[:_MAX_MARKDOWN_PREVIEW_ROWS]
    for row_idx, row in enumerate(preview_rows, start=2):
        row_cells = [f"`{row_idx}`"]
        for col in columns:
            val = row.get(col.field_name)
            badge_str = _format_cell_badge(col.field_name, val)
            if badge_str is not None:
                cell_str = badge_str
            elif val is None:
                cell_str = "`NULL`"
            elif isinstance(val, bool):
                cell_str = "`TRUE`" if val else "`FALSE`"
            elif isinstance(val, float):
                cell_str = (
                    f"{val:.2f}".rstrip("0").rstrip(".")
                    if "." in f"{val:.2f}"
                    else str(val)
                )
            else:
                cell_str = str(val).replace("|", "\\|").replace("\n", " ")
            row_cells.append(cell_str)
        md_lines.append("| " + " | ".join(row_cells) + " |")

    if total_rows > _MAX_MARKDOWN_PREVIEW_ROWS:
        trunc_cells = ["`...`"] + [
            f"*(Showing top {_MAX_MARKDOWN_PREVIEW_ROWS} of {total_rows} rows)*"
            if idx == 0
            else "..."
            for idx in range(len(columns))
        ]
        md_lines.append("| " + " | ".join(trunc_cells) + " |")

    # Append Formula Summary Footer Row in Markdown table
    footer_cells = ["**`fx`**"]
    for idx, col in enumerate(columns):
        fname = col.field_name
        if idx == 0:
            footer_cells.append(f"**`{footer.row_count_formula}` → `{footer.total_rows} rows`**")
        elif fname == sum_col:
            footer_cells.append(
                f"**`{footer.sum_logged_man_hours_formula}`**"
            )
        elif fname == avg_col:
            footer_cells.append(
                f"**`{footer.avg_estimated_mttr_hours_formula}`**"
            )
        else:
            footer_cells.append("—")
    md_lines.append("| " + " | ".join(footer_cells) + " |")

    md_lines.extend(
        [
            "",
            (
                f"**Formula Summary Bar:** `{footer.row_count_formula} = {footer.total_rows}` · "
                f"`{footer.sum_logged_man_hours_formula}` · "
                f"`{footer.avg_estimated_mttr_hours_formula}`"
            ),
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
        table_fqn=resolved_table_fqn,
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
        "table_fqn": resolved_table_fqn,
        "referenced_tables": referenced_tables,
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
