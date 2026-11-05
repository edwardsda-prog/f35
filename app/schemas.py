"""Pydantic v2 data contracts for UC0 Maintenance Data, UC1 Analytics, and UC2 JTD Search.

Provides strict schema validation for BigQuery maintenance work orders / Spreadsheet Cards,
telemetry/inventory records, Vega-Lite v5 visualizations, and S1000D JTD citations.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ActuatorReadinessRecord(BaseModel):
    """UC1 airframe actuator fatigue and mission capability record."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    tail_number: str = Field(..., min_length=1)
    part_serial_number: str = Field(default="ACT-99812-F")
    nsn: str = Field(default="1680-01-619-4821")
    base_location: str = Field(default="RAF Marham")
    current_flight_hours: float = Field(..., ge=0.0)
    life_limit_threshold_hrs: float = Field(..., gt=0.0)
    hours_remaining: float = Field(default=0.0)
    mission_capable_status: str = Field(default="PMC-M")

    @model_validator(mode="before")
    @classmethod
    def _compute_hours_remaining(cls, data: Any) -> Any:
        if isinstance(data, dict):
            curr = data.get("current_flight_hours")
            limit = data.get("life_limit_threshold_hrs")
            if curr is not None and limit is not None and "hours_remaining" not in data:
                data = dict(data)
                data["hours_remaining"] = round(float(limit) - float(curr), 4)
        return data


class VegaLiteSpec(BaseModel):
    """Vega-Lite v5 specification wrapper for inline Gemini Enterprise Canvas rendering."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_url: str = Field(
        default="https://vega.github.io/schema/vega-lite/v5.json",
        alias="$schema",
    )
    title: str | dict[str, Any] = Field(...)
    data: dict[str, Any] = Field(...)
    mark: str | dict[str, Any] | None = Field(default="bar")
    encoding: dict[str, Any] | None = Field(default=None)
    layer: list[dict[str, Any]] | None = Field(default=None)


VegaLiteChartSpec = VegaLiteSpec


class SortieSwapRecommendation(BaseModel):
    """UC1 sortie tail-swap and regional depot replenishment recommendation."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    sortie_id: str = Field(..., min_length=1)
    primary_tail: str = Field(..., min_length=1)
    spare_tail: str = Field(..., min_length=1)
    pilot_callsign: str = Field(default="Flt Lt Henderson / VIPER-1")
    supply_nsn: str = Field(default="1680-01-619-4821")
    depot_quantity_on_hand: int = Field(default=4, ge=0)
    depot_quantity_reserved_30d: int = Field(default=2, ge=0)
    shipping_eta_hours: float = Field(default=18.0, ge=0.0)
    action_status: str = Field(default="RECOMMENDED_SWAP_AND_REPLENISH")


class UC1AnalyticsOutput(BaseModel):
    """Composite UC1 analytics output contract."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    actuator_records: list[ActuatorReadinessRecord] = Field(default_factory=list)
    swap_recommendation: SortieSwapRecommendation | None = Field(default=None)
    vega_lite_charts: dict[str, VegaLiteSpec | dict[str, Any]] = Field(
        default_factory=dict
    )


class JtdCitation(BaseModel):
    """UC2 S1000D Joint Technical Data & Maintenance Narrative verbatim citation."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    doc_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    uri: str = Field(..., min_length=1)
    publication_code: str = Field(default="F35-AAA-000-00-00-00A-040A-A")
    service_branch_origin: str = Field(default="RAF")
    bit_fault_associated: bool = Field(default=False)
    snippet: str = Field(default="")
    markdown_link: str = Field(default="")

    @model_validator(mode="before")
    @classmethod
    def _populate_markdown_link(cls, data: Any) -> Any:
        if isinstance(data, dict):
            doc_id = data.get("doc_id", "")
            title = data.get("title", "")
            uri = data.get("uri", "")
            if not data.get("markdown_link") and doc_id and title and uri:
                data = dict(data)
                data["markdown_link"] = f"[{doc_id}: {title}]({uri})"
        return data


class UC2SearchOutput(BaseModel):
    """Composite UC2 grounded search output contract."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    original_query: str = Field(default="")
    normalized_query: str = Field(default="")
    results: list[JtdCitation] = Field(default_factory=list)
    citations: list[str] = Field(default_factory=list)


class SpreadsheetColumnHeader(BaseModel):
    """UC0 Excel / Google Sheets column header metadata with column letter A..R."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    column_letter: str = Field(..., min_length=1)
    col_letter: str = Field(default="")
    field_name: str = Field(..., min_length=1)
    display_label: str = Field(default="")
    data_type: str = Field(default="STRING")
    description: str = Field(default="")


class SpreadsheetFormulaFooter(BaseModel):
    """UC0 Excel / Google Sheets formula summary footer row."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    row_count_formula: str = Field(default="=COUNTA(A2:A15)")
    total_rows: int = Field(default=0, ge=0)
    sum_logged_man_hours_formula: str = Field(default="=SUM(logged_man_hours)")
    total_man_hours_formula: str = Field(default="=SUM(logged_man_hours)")
    sum_logged_man_hours: float = Field(default=0.0, ge=0.0)
    avg_estimated_mttr_hours_formula: str = Field(default="=AVERAGE(estimated_mttr_hours)")
    avg_mttr_hours_formula: str = Field(default="=AVERAGE(estimated_mttr_hours)")
    avg_estimated_mttr_hours: float = Field(default=0.0, ge=0.0)
    micap_count_formula: str = Field(default='=COUNTIF(aircraft_status, "NMC-S")')


class MaintenanceSpreadsheetCard(BaseModel):
    """UC0 interactive Excel / Google Sheets-like Spreadsheet Card & CSV export model."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    sheet_id: str = Field(default="F35_ODIN_Maintenance_Work_Orders")
    sheet_title: str = Field(default="F35_ODIN_Maintenance_Work_Orders")
    table_fqn: str = Field(
        default="antig-dave.ukd_f35_sustainment_demo.maintenance_work_orders"
    )
    bq_location: str = Field(default="EU")
    executed_sql: str = Field(..., min_length=1)
    execution_source: str = Field(default="BIGQUERY_EU")
    execution_latency_ms: float = Field(default=0.0, ge=0.0)
    row_count: int = Field(default=0, ge=0)
    column_count: int = Field(default=0, ge=0)
    columns: list[SpreadsheetColumnHeader] = Field(default_factory=list)
    rows: list[dict[str, Any]] = Field(default_factory=list)
    formula_footer: SpreadsheetFormulaFooter = Field(
        default_factory=SpreadsheetFormulaFooter
    )
    csv_gcs_uri: str = Field(default="")
    csv_download_url: str = Field(default="")
    spreadsheet_card_markdown: str = Field(default="")

