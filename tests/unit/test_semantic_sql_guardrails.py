"""Deterministic unit test suite for Generalized Semantic SQL Guardrails & Cross-Table Consistency (ISS-013).

Covers:
1. `TestIssueDocumentCSGExactReproduction` (`gs://f35sa/Issue Document.md`):
   - Exact 6-row, 6-column reproduction for Carrier Strike Group urgent maintenance jobs & grounded aircraft ordered by MTTR.
   - Automatic `CSG_ENTERPRISE_LOCATION_EXPANSION` recovery when an LLM passes `WHERE base_location = 'HMS Queen Elizabeth'` on a CSG/Fleet query.
2. `TestGeneralizedSemanticSQLCanonicalizer`:
   - 20+ unseen natural-language and SQL semantic variations across `base_location`, `squadron`, `work_order_status`, `aircraft_status`, `priority`, `fault_severity`, `bit_trigger_type`, `bay_dispatch_status`, `tool_calibration_status`, `shift_code`, and zero-row fuzzy substring auto-recovery.
3. `TestCrossTableWarehouseConsistency`:
   - 9-table, 900-row F-35 Data Warehouse completeness (`100` rows per table).
   - `ZM159` (`HMS Queen Elizabeth`) location consistency across telemetry, work orders (`WO-2026-88411`), PHM/BIT fault events (`PHM-2026-99111`, `PHM-2026-99113`), and SQEP/tooling (`RES-2026-00011`).
   - Full foreign-key referential integrity across `maintenance_work_orders`, `phm_bit_fault_events`, and `work_center_tooling_and_sqep`.
"""

from __future__ import annotations

import inspect
from typing import Any

import pytest


class DummyUserContentPart:
    """Mock GenAI Part with text."""

    def __init__(self, text: str) -> None:
        self.text = text


class DummyUserContent:
    """Mock GenAI Content with parts."""

    def __init__(self, text: str, role: str = "user") -> None:
        self.role = role
        self.parts = [DummyUserContentPart(text)]


class DummyToolContext:
    """Mock ADK ToolContext with mutable session state and user content."""

    def __init__(
        self,
        state: dict[str, Any] | None = None,
        user_text: str = "",
        invocation_id: str = "inv-iss013",
    ) -> None:
        self.state: dict[str, Any] = state if state is not None else {}
        self.user_content = DummyUserContent(user_text) if user_text else None
        self.invocation_id = invocation_id


@pytest.fixture(autouse=True)
def _force_local_sqlite_warehouse(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure deterministic, sub-millisecond SQLite execution against authoritative seed records."""
    import app.clients as clients_mod
    import app.tools.uc0_maintenance as uc0_mod

    monkeypatch.setattr(uc0_mod, "USE_CLOUD_CLIENTS", False)
    monkeypatch.setattr(clients_mod, "USE_CLOUD_CLIENTS", False)
    if hasattr(uc0_mod, "_init_in_memory_sqlite"):
        uc0_mod._init_in_memory_sqlite()


def _invoke_canonicalize(
    sql_query: str,
    sheet_title: str = "F35_ODIN_Maintenance_Work_Orders",
    tool_context: Any = None,
    user_intent_text: str = "",
) -> tuple[str, list[str]]:
    """Invoke `canonicalize_maintenance_sql` accommodating flexible signatures and return types."""
    from app.tools import uc0_maintenance

    fn = getattr(uc0_maintenance, "canonicalize_maintenance_sql")
    sig = inspect.signature(fn)
    kwargs: dict[str, Any] = {}
    for candidate_key, candidate_val in (
        ("sheet_title", sheet_title),
        ("tool_context", tool_context),
        ("user_intent_text", user_intent_text),
        ("user_text", user_intent_text),
        ("intent_text", user_intent_text),
    ):
        if candidate_key in sig.parameters and candidate_val:
            kwargs[candidate_key] = candidate_val

    result = fn(sql_query, **kwargs)
    if isinstance(result, tuple):
        canonical_sql = str(result[0])
        applied = list(result[1]) if len(result) > 1 and result[1] is not None else []
        return canonical_sql, applied
    if isinstance(result, dict):
        canonical_sql = str(
            result.get("canonical_sql") or result.get("sql") or sql_query
        )
        applied = list(
            result.get("canonicalization_applied")
            or result.get("applied_rules")
            or []
        )
        return canonical_sql, applied
    return str(result), []


# ===========================================================================
# 1. Issue Document Exact CSG Reproduction (`gs://f35sa/Issue Document.md`)
# ===========================================================================


class TestIssueDocumentCSGExactReproduction:
    """Verify exact 6-row, 6-column reproduction for the Carrier Strike Group prompt in `Issue Document.md`."""

    EXPECTED_CSG_COLUMNS: list[str] = [
        "work_order_id",
        "tail_number",
        "base_location",
        "aircraft_status",
        "work_order_status",
        "estimated_mttr_hours",
    ]

    EXPECTED_CSG_ROWS: list[tuple[str, str, str, str, str, float]] = [
        (
            "WO-2026-88405",
            "ZM153",
            "RAF Marham",
            "NMC-M",
            "IN_PROGRESS",
            14.5,
        ),
        (
            "WO-2026-88403",
            "ZM151",
            "RAF Marham",
            "PMC-M",
            "AWAITING_ENGINEERING_DISPOSITION",
            12.0,
        ),
        (
            "WO-2026-88411",
            "ZM159",
            "HMS Queen Elizabeth",
            "NMC-M",
            "OPEN",
            8.0,
        ),
        (
            "WO-2026-88414",
            "ZM162",
            "RAF Marham",
            "NMC-S",
            "AWAITING_PARTS (MICAP)",
            6.5,
        ),
        (
            "WO-2026-88404",
            "ZM152",
            "RAF Marham",
            "NMC-S",
            "AWAITING_PARTS (MICAP)",
            6.0,
        ),
        (
            "WO-2026-88408",
            "ZM156",
            "HMS Queen Elizabeth",
            "NMC-S",
            "AWAITING_PARTS (MICAP)",
            5.0,
        ),
    ]

    def test_canonical_csg_urgent_maintenance_query_exact_6_rows_and_columns(
        self,
    ) -> None:
        """Verify the canonical CSG urgent maintenance query returns the exact 6 rows and 6 columns in MTTR order."""
        from app.tools.uc0_maintenance import execute_maintenance_sql

        canonical_sql = (
            "SELECT work_order_id, tail_number, base_location, aircraft_status, "
            "work_order_status, estimated_mttr_hours "
            "FROM `antig-dave.ukd_f35_sustainment_demo.maintenance_work_orders` "
            "WHERE priority = 'PRIORITY_1_RED_X' AND work_order_status != 'COMPLETED' "
            "ORDER BY estimated_mttr_hours DESC"
        )
        res = execute_maintenance_sql(
            canonical_sql,
            sheet_title="CSG_Urgent_Maintenance_Jobs",
        )

        assert res["status"] == "SUCCESS"
        assert res["row_count"] == 6
        assert res["column_count"] == 6

        col_names = [c["field_name"] for c in res["columns"]]
        assert col_names == self.EXPECTED_CSG_COLUMNS

        actual_rows = [
            (
                str(r["work_order_id"]),
                str(r["tail_number"]),
                str(r["base_location"]),
                str(r["aircraft_status"]),
                str(r["work_order_status"]),
                float(r["estimated_mttr_hours"]),
            )
            for r in res["rows"]
        ]
        assert actual_rows == self.EXPECTED_CSG_ROWS

    def test_buggy_issue_document_query_auto_expands_csg_location(self) -> None:
        """Verify the buggy query from `Issue Document.md` strips `base_location = 'HMS Queen Elizabeth'` and returns all 6 CSG rows."""
        from app.tools.uc0_maintenance import execute_maintenance_sql

        buggy_sql = (
            "SELECT work_order_id, tail_number, base_location, aircraft_status, "
            "work_order_status, estimated_mttr_hours "
            "FROM `antig-dave.ukd_f35_sustainment_demo.maintenance_work_orders` "
            "WHERE base_location = 'HMS Queen Elizabeth' "
            "AND priority = 'PRIORITY_1_RED_X' "
            "AND work_order_status != 'COMPLETED' "
            "ORDER BY estimated_mttr_hours DESC"
        )

        # 1. Verify via sheet_title="CSG_Urgent_Maintenance_Jobs"
        canonical_sql, applied_rules = _invoke_canonicalize(
            buggy_sql,
            sheet_title="CSG_Urgent_Maintenance_Jobs",
        )
        assert "HMS Queen Elizabeth" not in canonical_sql
        assert any("CSG" in rule.upper() for rule in applied_rules)

        res_by_title = execute_maintenance_sql(
            buggy_sql,
            sheet_title="CSG_Urgent_Maintenance_Jobs",
        )
        assert res_by_title["status"] == "SUCCESS"
        assert res_by_title["row_count"] == 6
        actual_by_title = [
            (
                str(r["work_order_id"]),
                str(r["tail_number"]),
                str(r["base_location"]),
                str(r["aircraft_status"]),
                str(r["work_order_status"]),
                float(r["estimated_mttr_hours"]),
            )
            for r in res_by_title["rows"]
        ]
        assert actual_by_title == self.EXPECTED_CSG_ROWS

        # 2. Verify via ToolContext carrying the user prompt from Issue Document.md
        ctx = DummyToolContext(
            user_text=(
                "What are our most urgent maintenance jobs and grounded aircraft "
                "across the Carrier Strike Group right now, ordered by how long they will take to fix?"
            )
        )
        res_by_ctx = execute_maintenance_sql(
            buggy_sql,
            sheet_title="Urgent_Maintenance_Jobs",
            tool_context=ctx,
        )
        assert res_by_ctx["status"] == "SUCCESS"
        assert res_by_ctx["row_count"] == 6
        actual_by_ctx = [
            (
                str(r["work_order_id"]),
                str(r["tail_number"]),
                str(r["base_location"]),
                str(r["aircraft_status"]),
                str(r["work_order_status"]),
                float(r["estimated_mttr_hours"]),
            )
            for r in res_by_ctx["rows"]
        ]
        assert actual_by_ctx == self.EXPECTED_CSG_ROWS


# ===========================================================================
# 2. Generalized Semantic SQL Canonicalizer (20+ Unseen Semantic Variations)
# ===========================================================================


class TestGeneralizedSemanticSQLCanonicalizer:
    """Verify `canonicalize_maintenance_sql` and `execute_maintenance_sql` across 20+ unseen semantic SQL variations."""

    @pytest.mark.parametrize(
        "location_synonym",
        ["AFLOAT", "EMBARKED", "AT_SEA", "CARRIER"],
    )
    def test_afloat_location_categories(self, location_synonym: str) -> None:
        """Verify AFLOAT/EMBARKED/AT_SEA/CARRIER expand to Queen Elizabeth Class carriers."""
        from app.tools.uc0_maintenance import execute_maintenance_sql

        sql = (
            "SELECT work_order_id, tail_number, base_location, work_order_status "
            f"FROM maintenance_work_orders WHERE base_location = '{location_synonym}'"
        )
        canonical_sql, _ = _invoke_canonicalize(sql)
        assert "HMS Queen Elizabeth" in canonical_sql
        assert "HMS Prince of Wales" in canonical_sql

        res = execute_maintenance_sql(sql)
        assert res["status"] == "SUCCESS"
        assert res["row_count"] > 0
        for row in res["rows"]:
            assert row["base_location"] in {
                "HMS Queen Elizabeth",
                "HMS Prince of Wales",
            }

    @pytest.mark.parametrize(
        "shore_synonym",
        ["MOB", "ASHORE", "HOME_STATION", "MARHAM"],
    )
    def test_shore_location_categories(self, shore_synonym: str) -> None:
        """Verify MOB/ASHORE/HOME_STATION/MARHAM normalize to `'RAF Marham'`."""
        from app.tools.uc0_maintenance import execute_maintenance_sql

        sql = (
            "SELECT work_order_id, tail_number, base_location "
            f"FROM maintenance_work_orders WHERE base_location = '{shore_synonym}' "
            "AND work_order_status != 'COMPLETED'"
        )
        canonical_sql, _ = _invoke_canonicalize(sql)
        assert "RAF Marham" in canonical_sql

        res = execute_maintenance_sql(sql)
        assert res["status"] == "SUCCESS"
        assert res["row_count"] > 0
        assert all(r["base_location"] == "RAF Marham" for r in res["rows"])

    @pytest.mark.parametrize(
        ("ship_alias", "expected_ship"),
        [
            ("QNLZ", "HMS Queen Elizabeth"),
            ("HMS QE", "HMS Queen Elizabeth"),
            ("PWLS", "HMS Prince of Wales"),
            ("HMS PoW", "HMS Prince of Wales"),
        ],
    )
    def test_ship_hull_aliases(self, ship_alias: str, expected_ship: str) -> None:
        """Verify Royal Navy carrier hull codes and shorthand aliases map to canonical carrier names."""
        from app.tools.uc0_maintenance import execute_maintenance_sql

        sql = (
            "SELECT work_order_id, tail_number, base_location "
            f"FROM maintenance_work_orders WHERE base_location = '{ship_alias}'"
        )
        canonical_sql, _ = _invoke_canonicalize(sql)
        assert expected_ship in canonical_sql

        res = execute_maintenance_sql(sql)
        assert res["status"] == "SUCCESS"
        assert res["row_count"] > 0
        assert all(r["base_location"] == expected_ship for r in res["rows"])

    @pytest.mark.parametrize(
        ("sqn_shorthand", "expected_sqn"),
        [
            ("617 Squadron", "617 Sqn (The Dambusters)"),
            ("Dambusters", "617 Sqn (The Dambusters)"),
            ("809 NAS", "809 NAS (The Immortals)"),
            ("Immortals", "809 NAS (The Immortals)"),
            ("207 Squadron", "207 Sqn (OCU)"),
            ("OCU", "207 Sqn (OCU)"),
        ],
    )
    def test_squadron_shorthand_aliases(
        self, sqn_shorthand: str, expected_sqn: str
    ) -> None:
        """Verify squadron numbers, nicknames, and unit types map to canonical squadron strings."""
        from app.tools.uc0_maintenance import execute_maintenance_sql

        sql = (
            "SELECT work_order_id, tail_number, squadron "
            f"FROM maintenance_work_orders WHERE squadron = '{sqn_shorthand}'"
        )
        canonical_sql, _ = _invoke_canonicalize(sql)
        assert expected_sqn in canonical_sql

        res = execute_maintenance_sql(sql)
        assert res["status"] == "SUCCESS"
        assert res["row_count"] > 0
        assert all(r["squadron"] == expected_sqn for r in res["rows"])

    @pytest.mark.parametrize("lifecycle_synonym", ["ACTIVE", "BACKLOG"])
    def test_work_order_lifecycle_active_and_backlog(
        self, lifecycle_synonym: str
    ) -> None:
        """Verify ACTIVE and BACKLOG expand to `work_order_status != 'COMPLETED'` (10 active rows)."""
        from app.tools.uc0_maintenance import execute_maintenance_sql

        sql = (
            "SELECT work_order_id, tail_number, work_order_status "
            f"FROM maintenance_work_orders WHERE work_order_status = '{lifecycle_synonym}'"
        )
        res = execute_maintenance_sql(sql)
        assert res["status"] == "SUCCESS"
        assert res["row_count"] == 10
        assert all(r["work_order_status"] != "COMPLETED" for r in res["rows"])

    def test_work_order_lifecycle_micap_and_open_backlog_expansion(self) -> None:
        """Verify `work_order_status = 'MICAP'` and `work_order_status = 'OPEN'` with active/backlog sheet title."""
        from app.tools.uc0_maintenance import execute_maintenance_sql

        sql_micap = (
            "SELECT work_order_id, tail_number, work_order_status "
            "FROM maintenance_work_orders WHERE work_order_status = 'MICAP'"
        )
        res_micap = execute_maintenance_sql(sql_micap)
        assert res_micap["status"] == "SUCCESS"
        assert res_micap["row_count"] == 3
        assert all(
            r["work_order_status"] == "AWAITING_PARTS (MICAP)"
            for r in res_micap["rows"]
        )

        sql_open = (
            "SELECT work_order_id, tail_number, work_order_status "
            "FROM maintenance_work_orders WHERE work_order_status = 'OPEN'"
        )
        res_open_backlog = execute_maintenance_sql(
            sql_open,
            sheet_title="CSG_Active_Backlog",
        )
        assert res_open_backlog["status"] == "SUCCESS"
        assert res_open_backlog["row_count"] == 10
        assert all(
            r["work_order_status"] != "COMPLETED" for r in res_open_backlog["rows"]
        )

    @pytest.mark.parametrize(
        ("status_synonym", "expected_statuses", "expected_active_count"),
        [
            ("GROUNDED", {"NMC-M", "NMC-S"}, 5),
            ("NMC", {"NMC-M", "NMC-S"}, 5),
            ("DOWN", {"NMC-M", "NMC-S"}, 5),
            ("MICAP", {"NMC-S"}, 3),
            ("PMC", {"PMC-M"}, 5),
        ],
    )
    def test_aircraft_readiness_synonyms_active(
        self,
        status_synonym: str,
        expected_statuses: set[str],
        expected_active_count: int,
    ) -> None:
        """Verify GROUNDED, NMC, DOWN, MICAP, and PMC map to canonical `aircraft_status` values."""
        from app.tools.uc0_maintenance import execute_maintenance_sql

        sql = (
            "SELECT work_order_id, tail_number, aircraft_status "
            f"FROM maintenance_work_orders WHERE aircraft_status = '{status_synonym}' "
            "AND work_order_status != 'COMPLETED'"
        )
        res = execute_maintenance_sql(sql)
        assert res["status"] == "SUCCESS"
        assert res["row_count"] == expected_active_count
        assert all(r["aircraft_status"] in expected_statuses for r in res["rows"])

    def test_aircraft_readiness_serviceable_synonym(self) -> None:
        """Verify `aircraft_status = 'SERVICEABLE'` maps to `'FMC'`."""
        from app.tools.uc0_maintenance import execute_maintenance_sql

        sql = (
            "SELECT work_order_id, tail_number, aircraft_status "
            "FROM maintenance_work_orders WHERE aircraft_status = 'SERVICEABLE'"
        )
        res = execute_maintenance_sql(sql)
        assert res["status"] == "SUCCESS"
        assert res["row_count"] > 0
        assert all(r["aircraft_status"] == "FMC" for r in res["rows"])

    @pytest.mark.parametrize(
        ("priority_synonym", "expected_priority", "expected_active_count"),
        [
            ("P1", "PRIORITY_1_RED_X", 6),
            ("RED_X", "PRIORITY_1_RED_X", 6),
            ("CRITICAL", "PRIORITY_1_RED_X", 6),
            ("P2", "PRIORITY_2_URGENT", 4),
            ("URGENT", "PRIORITY_2_URGENT", 4),
        ],
    )
    def test_priority_synonyms_active(
        self,
        priority_synonym: str,
        expected_priority: str,
        expected_active_count: int,
    ) -> None:
        """Verify P1, RED_X, CRITICAL, P2, and URGENT map to canonical `priority` enums."""
        from app.tools.uc0_maintenance import execute_maintenance_sql

        sql = (
            "SELECT work_order_id, tail_number, priority "
            f"FROM maintenance_work_orders WHERE priority = '{priority_synonym}' "
            "AND work_order_status != 'COMPLETED'"
        )
        res = execute_maintenance_sql(sql)
        assert res["status"] == "SUCCESS"
        assert res["row_count"] == expected_active_count
        assert all(r["priority"] == expected_priority for r in res["rows"])

    def test_priority_routine_synonym(self) -> None:
        """Verify `priority = 'ROUTINE'` maps to `'PRIORITY_3_ROUTINE'`."""
        from app.tools.uc0_maintenance import execute_maintenance_sql

        sql = (
            "SELECT work_order_id, tail_number, priority "
            "FROM maintenance_work_orders WHERE priority = 'ROUTINE'"
        )
        res = execute_maintenance_sql(sql)
        assert res["status"] == "SUCCESS"
        assert res["row_count"] > 0
        assert all(r["priority"] == "PRIORITY_3_ROUTINE" for r in res["rows"])

    @pytest.mark.parametrize(
        ("col_name", "synonym_val", "expected_canonical"),
        [
            ("fault_severity", "CRITICAL", "CRITICAL_GROUNDING"),
            ("fault_severity", "NO_BIT", "NO_BIT_FAULT_LOGGED"),
            ("bit_trigger_type", "ZERO_BIT", "PILOT_REPORT_ONLY_NO_BIT"),
            ("bit_trigger_type", "PILOT_REPORT", "PILOT_REPORT_ONLY_NO_BIT"),
        ],
    )
    def test_phm_bit_fault_event_synonyms(
        self, col_name: str, synonym_val: str, expected_canonical: str
    ) -> None:
        """Verify PHM/BIT fault severity and trigger type synonyms on `phm_bit_fault_events`."""
        from app.tools.uc0_maintenance import execute_maintenance_sql

        sql = (
            f"SELECT fault_event_id, tail_number, {col_name} "
            f"FROM phm_bit_fault_events WHERE {col_name} = '{synonym_val}'"
        )
        res = execute_maintenance_sql(sql)
        assert res["status"] == "SUCCESS"
        assert res["row_count"] > 0
        assert all(r[col_name] == expected_canonical for r in res["rows"])

    @pytest.mark.parametrize("dispatch_synonym", ["BLOCKED", "HELD_UP"])
    def test_tooling_bay_dispatch_blocked_synonyms(
        self, dispatch_synonym: str
    ) -> None:
        """Verify `bay_dispatch_status = 'BLOCKED'` and `'HELD_UP'` expand to all 3 blocked dispatch states."""
        from app.tools.uc0_maintenance import execute_maintenance_sql

        sql = (
            "SELECT resource_id, assigned_work_order_id, bay_dispatch_status "
            f"FROM work_center_tooling_and_sqep WHERE bay_dispatch_status = '{dispatch_synonym}'"
        )
        res = execute_maintenance_sql(sql)
        assert res["status"] == "SUCCESS"
        assert res["row_count"] > 0
        assert all(
            str(r["bay_dispatch_status"]).startswith("BLOCKED_")
            for r in res["rows"]
        )

    @pytest.mark.parametrize("cal_synonym", ["EXPIRED", "OUT_OF_CAL"])
    def test_tooling_calibration_expired_synonyms(self, cal_synonym: str) -> None:
        """Verify `tool_calibration_status = 'EXPIRED'` and `'OUT_OF_CAL'` map to `'EXPIRED_OUT_OF_CAL'`."""
        from app.tools.uc0_maintenance import execute_maintenance_sql

        sql = (
            "SELECT resource_id, required_special_tool_id, tool_calibration_status "
            f"FROM work_center_tooling_and_sqep WHERE tool_calibration_status = '{cal_synonym}'"
        )
        res = execute_maintenance_sql(sql)
        assert res["status"] == "SUCCESS"
        assert res["row_count"] > 0
        assert all(
            r["tool_calibration_status"] == "EXPIRED_OUT_OF_CAL"
            for r in res["rows"]
        )

    @pytest.mark.parametrize(
        ("shift_synonym", "expected_shift"),
        [
            ("DAY", "DAY_ALPHA"),
            ("NIGHT", "NIGHT_BRAVO"),
            ("CARRIER", "CARRIER_WATCH_1"),
        ],
    )
    def test_tooling_shift_code_synonyms(
        self, shift_synonym: str, expected_shift: str
    ) -> None:
        """Verify `shift_code` shorthand values (`DAY`, `NIGHT`, `CARRIER`) map to canonical shift codes."""
        from app.tools.uc0_maintenance import execute_maintenance_sql

        sql = (
            "SELECT resource_id, shift_code "
            f"FROM work_center_tooling_and_sqep WHERE shift_code = '{shift_synonym}'"
        )
        res = execute_maintenance_sql(sql)
        assert res["status"] == "SUCCESS"
        assert res["row_count"] > 0
        assert all(r["shift_code"] == expected_shift for r in res["rows"])

    def test_zero_row_fuzzy_substring_auto_recovery(self) -> None:
        """Verify exact equality on descriptive text (`subsystem_name = 'Canopy Latch'`) auto-recovers via LIKE."""
        from app.tools.uc0_maintenance import execute_maintenance_sql

        sql = (
            "SELECT work_order_id, tail_number, subsystem_name "
            "FROM maintenance_work_orders WHERE subsystem_name = 'Canopy Latch'"
        )
        res = execute_maintenance_sql(sql)
        assert res["status"] == "SUCCESS"
        assert res["row_count"] > 0
        assert all(
            "canopy latch" in str(r["subsystem_name"]).lower()
            for r in res["rows"]
        )


# ===========================================================================
# 3. Cross-Table Warehouse Consistency (900 Records Across 9 Tables)
# ===========================================================================


class TestCrossTableWarehouseConsistency:
    """Verify 9-table seed counts, `ZM159` carrier consistency, and foreign-key referential integrity."""

    def test_all_9_tables_have_100_rows_900_total(self) -> None:
        """Verify all 9 tables in `app/seed_data/bq_seed_records.py` have 100 rows each (900 total)."""
        from app.seed_data.bq_seed_records import BQ_SEED_TABLES

        assert len(BQ_SEED_TABLES) == 9
        total_records = 0
        for table_name, rows in BQ_SEED_TABLES.items():
            assert len(rows) == 100, (
                f"Expected 100 rows in {table_name}, found {len(rows)}"
            )
            total_records += len(rows)
        assert total_records == 900

    def test_zm159_hms_queen_elizabeth_consistency_across_all_tables(self) -> None:
        """Verify `ZM159` has `base_location == 'HMS Queen Elizabeth'` across Tables 1, 7, 8, and 9."""
        from app.seed_data.bq_seed_records import (
            AIRFRAME_COMPONENT_TELEMETRY_ROWS,
            MAINTENANCE_WORK_ORDERS_ROWS,
            PHM_BIT_FAULT_EVENTS_ROWS,
            WORK_CENTER_TOOLING_AND_SQEP_ROWS,
        )

        # Table 1: airframe_component_telemetry
        zm159_telemetry = [
            r
            for r in AIRFRAME_COMPONENT_TELEMETRY_ROWS
            if r["tail_number"] == "ZM159"
        ]
        assert len(zm159_telemetry) >= 1
        for r in zm159_telemetry:
            assert r["base_location"] == "HMS Queen Elizabeth"

        # Table 7: maintenance_work_orders (WO-2026-88411)
        wo_88411 = next(
            r
            for r in MAINTENANCE_WORK_ORDERS_ROWS
            if r["work_order_id"] == "WO-2026-88411"
        )
        assert wo_88411["tail_number"] == "ZM159"
        assert wo_88411["base_location"] == "HMS Queen Elizabeth"
        assert "HMS Queen Elizabeth" in wo_88411["discrepancy_narrative"]

        # Table 8: phm_bit_fault_events (PHM-2026-99111, PHM-2026-99113)
        for fault_id in ("PHM-2026-99111", "PHM-2026-99113"):
            phm_row = next(
                r
                for r in PHM_BIT_FAULT_EVENTS_ROWS
                if r["fault_event_id"] == fault_id
            )
            assert phm_row["tail_number"] == "ZM159"
            assert phm_row["base_location"] == "HMS Queen Elizabeth"

        # Table 9: work_center_tooling_and_sqep (RES-2026-00011)
        res_00011 = next(
            r
            for r in WORK_CENTER_TOOLING_AND_SQEP_ROWS
            if r["resource_id"] == "RES-2026-00011"
        )
        assert res_00011["assigned_work_order_id"] == "WO-2026-88411"
        assert res_00011["base_location"] == "HMS Queen Elizabeth"

    def test_foreign_key_referential_integrity_across_uc0_tables(self) -> None:
        """Verify every linked work order in Tables 8 and 9 matches its parent work order in Table 7."""
        from app.seed_data.bq_seed_records import (
            MAINTENANCE_WORK_ORDERS_ROWS,
            PHM_BIT_FAULT_EVENTS_ROWS,
            WORK_CENTER_TOOLING_AND_SQEP_ROWS,
        )

        wo_by_id = {r["work_order_id"]: r for r in MAINTENANCE_WORK_ORDERS_ROWS}

        for res_row in WORK_CENTER_TOOLING_AND_SQEP_ROWS:
            wo_id = res_row.get("assigned_work_order_id")
            if wo_id:
                assert wo_id in wo_by_id, (
                    f"Resource {res_row['resource_id']} references unknown work_order_id {wo_id}"
                )
                parent_wo = wo_by_id[wo_id]
                assert res_row["base_location"] == parent_wo["base_location"], (
                    f"Location mismatch on {res_row['resource_id']} -> {wo_id}: "
                    f"{res_row['base_location']} != {parent_wo['base_location']}"
                )

        for phm_row in PHM_BIT_FAULT_EVENTS_ROWS:
            wo_id = phm_row.get("linked_work_order_id")
            if wo_id:
                assert wo_id in wo_by_id, (
                    f"PHM event {phm_row['fault_event_id']} references unknown work_order_id {wo_id}"
                )
                parent_wo = wo_by_id[wo_id]
                assert phm_row["tail_number"] == parent_wo["tail_number"], (
                    f"Tail mismatch on {phm_row['fault_event_id']} -> {wo_id}: "
                    f"{phm_row['tail_number']} != {parent_wo['tail_number']}"
                )
                assert phm_row["base_location"] == parent_wo["base_location"], (
                    f"Location mismatch on {phm_row['fault_event_id']} -> {wo_id}: "
                    f"{phm_row['base_location']} != {parent_wo['base_location']}"
                )
