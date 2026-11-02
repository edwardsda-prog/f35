"""Pydantic v2 data contracts for UC1 Analytics, UC2 JTD Search, and UC3 Airworthiness.

Provides strict schema validation for BigQuery telemetry/inventory records, Vega-Lite v5
visualizations, S1000D JTD citations, deterministic ASIP Miner's Rule fatigue results,
3D CAD flaw mappings, mBOM lot audits, MIL-STD-3001 SAR, and Form 700 HITL release packages.
"""

from __future__ import annotations

from typing import Any, Literal

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


class AsipFatigueResult(BaseModel):
    """UC3 deterministic Rainflow & Palmgren-Miner cumulative damage output (SAFE-01)."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    tail_number: str = Field(default="ZM151")
    structural_station_id: str = Field(default="Frame 496")
    mach_number: float = Field(default=1.3)
    peak_nz_g: float = Field(default=9.4)
    peak_egt_celsius: float = Field(default=220.0)
    miners_rule_damage_delta: float = Field(..., ge=0.0)
    calculated_yield_pct: float = Field(..., ge=0.0)
    yield_limit_pct: float = Field(default=100.0)
    exceeds_yield_limit: bool = Field(default=True)
    required_ndi_class: str = Field(default="CLASS_A_ULTRASONIC_C_SCAN")
    mandated_jtd_rule: str = Field(default="JTD Rule 53-11-00")
    compliance_standard: str = Field(default="MIL-HDBK-516C / DEF STAN 00-970")
    rainflow_cycles: list[dict[str, Any]] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def _compute_exceeds_yield(cls, data: Any) -> Any:
        if isinstance(data, dict):
            yield_pct = data.get("calculated_yield_pct")
            limit_pct = data.get("yield_limit_pct", 100.0)
            if yield_pct is not None and "exceeds_yield_limit" not in data:
                data = dict(data)
                data["exceeds_yield_limit"] = float(yield_pct) > float(limit_pct)
        return data


class CScanCadMappingResult(BaseModel):
    """UC3 Ultrasonic C-Scan anomaly extraction and 3D CAD station mapping result."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    c_scan_document_id: str = Field(default="DOC-06")
    srm_document_id: str = Field(default="DOC-05")
    mapped_cad_station: str = Field(default="Frame 496 — Fastener Hole #14")
    fastener_hole_id: str = Field(default="Hole #14")
    measured_ndi_elongation_in: float = Field(..., ge=0.0)
    allowable_elongation_in: float = Field(default=0.015, gt=0.0)
    within_allowable_limits: bool = Field(default=True)
    cad_coordinates_mm: dict[str, float] = Field(
        default_factory=lambda: {"fs_x": 4960.0, "bl_y": -342.5, "wl_z": 118.2}
    )
    disposition: str = Field(default="SERVICEABLE_WITH_TORQUE_RECHECK")
    mandated_jtd_task_card: str = Field(default="JTD Task Card 53-11-00-280")


class MbomFastenerAuditResult(BaseModel):
    """UC3 as-maintained mBOM fastener lot audit and global fleet exposure result."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    mbom_record_id: str = Field(default="MBOM-ZM151-F496-H14")
    tail_number: str = Field(default="ZM151")
    station_id: str = Field(default="Frame 496 — Fastener Hole #14")
    fastener_material_spec: str = Field(default="Ti-6Al-4V")
    fastener_lot_number: str = Field(default="Lot #8841-B")
    hours_since_install: float = Field(default=312.0, ge=0.0)
    allowable_elongation_in: float = Field(default=0.015, gt=0.0)
    measured_ndi_elongation_in: float = Field(default=0.012, ge=0.0)
    within_limits: bool = Field(default=True)
    global_fleet_affected_count: int = Field(default=14, ge=0)
    fleet_inspection_directive: str = Field(
        default="Proactive 30-day inspection across 14 global F-35 tails carrying Lot #8841-B"
    )


class StructuralAppraisalReport(BaseModel):
    """MIL-STD-3001 / DEF STAN 00-970 Structural Appraisal Report (SAR) model."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    sar_id: str = Field(default="SAR-20261102-ZM151")
    tail_number: str = Field(default="ZM151")
    station_id: str = Field(default="Frame 496 — Fastener Hole #14")
    compliance_standard: str = Field(default="MIL-STD-3001 / DEF STAN 00-970")
    telemetry_event_id: str = Field(default="EXC-20261102-ZM151")
    fatigue_result: AsipFatigueResult | dict[str, Any] | None = Field(default=None)
    cscan_mapping: CScanCadMappingResult | dict[str, Any] | None = Field(default=None)
    mbom_audit: MbomFastenerAuditResult | dict[str, Any] | None = Field(default=None)
    engineering_summary: str = Field(default="")


class Form700ReleasePackage(BaseModel):
    """Aircraft Form 700 / AFTO Form 781 airworthiness release package (SAFE-02)."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    release_package_id: str = Field(..., min_length=1)
    tail_number: str = Field(default="ZM151", min_length=1)
    station_id: str = Field(default="Frame 496 — Fastener Hole #14", min_length=1)
    appraisal_report_uri: str = Field(
        default="gs://antig-dave-f35-staging-europe-west1/unstructured/sar/SAR-20261102-ZM151.pdf",
        min_length=1,
    )
    mandated_jtd_task_card: str = Field(..., min_length=1)
    disposition_status: str = Field(..., min_length=1)
    hitl_reviewer_role: str = Field(default="Lead Stress Engineer", min_length=1)
    hitl_review_status: Literal["PENDING_HITL_REVIEW", "CONFIRMED_BY_ENGINEER"] = Field(
        default="PENDING_HITL_REVIEW"
    )
    compliance_standard: str = Field(default="MIL-STD-3001 / DEF STAN 00-970")
    staged_turn_id: int | str | None = Field(default=None)
    approved_turn_id: int | str | None = Field(default=None)
    approval_notes: str | None = Field(default=None)
