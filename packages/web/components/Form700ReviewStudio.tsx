/**
 * @fileoverview Form700ReviewStudio — UC3 MIL-STD-3001 Structural Appraisal Report (SAR)
 * & Aircraft Form 700 / AFTO Form 781 Human-in-the-Loop (HITL) Review Studio.
 *
 * Enforces mandatory safety and airworthiness invariants:
 * - SAFE-01 (Deterministic Structural Math Only): Strictly renders values passed via props
 *   from the agent response (`assess_airframe_airworthiness` / `generate_form700_airworthiness_package`).
 *   Never invents, estimates, or recalculates stress, yield percentages, Rainflow cycles,
 *   Palmgren-Miner cumulative damage (D = sum(n_i / N_i)), or C-scan elongation metrics.
 * - SAFE-02 (Mandatory Two-Turn HITL Release Gate): Blocks transition from
 *   `PENDING_HITL_REVIEW` to `CONFIRMED_BY_ENGINEER` in the same conversation turn
 *   (`currentTurnId <= stagedTurnId`) and requires explicit sign-off by an authorized
 *   engineering authority (`Lead Stress Engineer`, `Chief Airworthiness Engineer`,
 *   `Structural Integrity Lead`, or `CTO`) with non-empty engineering approval notes.
 */

import { React, VNode } from "./VegaCanvas";

export type HitlReviewStatus =
  | "PENDING_HITL_REVIEW"
  | "CONFIRMED_BY_ENGINEER"
  | "REJECTED_BY_ENGINEER";

export type DispositionStatus =
  | "SERVICEABLE_WITH_TORQUE_RECHECK"
  | "GROUNDED_AWAITING_NDI"
  | "UNSERVICEABLE_DEPOT_REPAIR"
  | string;

export type AuthorizedEngineeringRole =
  | "Lead Stress Engineer"
  | "Chief Airworthiness Engineer"
  | "Structural Integrity Lead"
  | "CTO";

export const AUTHORIZED_ENGINEERING_ROLES: readonly AuthorizedEngineeringRole[] = [
  "Lead Stress Engineer",
  "Chief Airworthiness Engineer",
  "Structural Integrity Lead",
  "CTO",
] as const;

/**
 * Card 1: 1553 Flight Bus Exceedance Synchronization (Task A).
 * Example authoritative props:
 * - exceedanceEventId: "EXC-20261102-ZM151"
 * - peakGLoad: 9.4 (G)
 * - machNumber: 1.3 (Mach)
 * - egtCelsius: 220.0 (°C)
 * - timestampUtc: "2026-11-02T14:22:18.420Z"
 * - durationSeconds: 3.2 (s)
 * - structuralStationId: "Frame 496"
 */
export interface FlightBusSyncDiagnostic {
  exceedanceEventId?: string;
  exceedance_event_id?: string;
  tailNumber?: string;
  tail_number?: string;
  peakGLoad?: number;
  peak_g_load?: number;
  machNumber?: number;
  mach_number?: number;
  egtCelsius?: number;
  egt_celsius?: number;
  timestampUtc?: string;
  timestamp_utc?: string;
  durationSeconds?: number;
  duration_seconds?: number;
  structuralStationId?: string;
  structural_station_id?: string;
  maneuverDescription?: string;
  maneuver_description?: string;
  busProtocol?: string;
}

/**
 * Card 2: Deterministic Palmgren-Miner & Rainflow Fatigue Analysis (Task B).
 * Example authoritative props:
 * - minersRuleDamageDelta: 0.0042 (D = sum(n_i / N_i))
 * - calculatedYieldPct: 104.2 (%)
 * - yieldLimitPct: 100.0 (%)
 * - requiredNdiAction: "CLASS_A_ULTRASONIC_C_SCAN"
 * - triggeredJtdRule: "JTD Rule 53-11-00"
 * - referenceDocId: "DOC-04"
 */
export interface MinersRuleFatigueDiagnostic {
  minersRuleDamageDelta?: number;
  miners_rule_damage_delta?: number;
  cumulativeDamageIndex?: number;
  cumulative_damage_index?: number;
  calculatedYieldPct?: number;
  calculated_yield_pct?: number;
  yieldLimitPct?: number;
  yield_limit_pct?: number;
  rainflowCyclesCounted?: number;
  rainflow_cycles_counted?: number;
  requiredNdiAction?: string;
  required_ndi_action?: string;
  triggeredJtdRule?: string;
  triggered_jtd_rule?: string;
  referenceDocId?: string;
  reference_doc_id?: string;
  governingStandard?: string;
}

/**
 * Card 3: Multimodal Ultrasonic C-Scan & 3D CAD Coordinate Join (Task C).
 * Example authoritative props:
 * - cScanDocumentId: "DOC-06"
 * - cadReferenceDocumentId: "DOC-05"
 * - srmChapter: "SRM Chapter 51-40"
 * - structuralStation: "Frame 496"
 * - fastenerHoleId: "Fastener Hole #14"
 * - measuredShearElongationIn: 0.012
 * - allowableElongationLimitIn: 0.015
 */
export interface UltrasonicCScanCadDiagnostic {
  cScanDocumentId?: string;
  c_scan_document_id?: string;
  cadReferenceDocumentId?: string;
  cad_reference_document_id?: string;
  srmChapter?: string;
  srm_chapter?: string;
  structuralStation?: string;
  structural_station?: string;
  fastenerHoleId?: string;
  fastener_hole_id?: string;
  measuredShearElongationIn?: number;
  measured_shear_elongation_in?: number;
  allowableElongationLimitIn?: number;
  allowable_elongation_limit_in?: number;
  cadCoordinatesMm?: { x: number; y: number; z: number };
  cad_coordinates_mm?: { x: number; y: number; z: number };
  withinAllowableTolerance?: boolean;
  within_allowable_tolerance?: boolean;
}

/**
 * Card 4: As-Maintained mBOM Fastener Lot Audit (Task D).
 * Example authoritative props:
 * - mbomRecordId: "MBOM-ZM151-F496-H14"
 * - materialAlloy: "Ti-6Al-4V"
 * - fastenerLotNumber: "Lot #8841-B"
 * - hoursSinceInstall: 312.0
 * - allowableLimitIn: 0.015
 * - globalFleetAffectedTailsCount: 14
 * - inspectionWindowDays: 30
 * - mandatedTaskCard: "JTD Task Card 53-11-00-280"
 */
export interface MbomFastenerLotAuditDiagnostic {
  mbomRecordId?: string;
  mbom_record_id?: string;
  materialAlloy?: string;
  material_alloy?: string;
  fastenerLotNumber?: string;
  fastener_lot_number?: string;
  hoursSinceInstall?: number;
  hours_since_install?: number;
  allowableLimitIn?: number;
  allowable_limit_in?: number;
  globalFleetAffectedTailsCount?: number;
  global_fleet_affected_tails_count?: number;
  inspectionWindowDays?: number;
  inspection_window_days?: number;
  mandatedTaskCard?: string;
  mandated_task_card?: string;
}

/**
 * Complete 4-Way ASIP Diagnostic bundle passed from the agent response.
 */
export interface AsipDiagnosticBundle {
  flightBusSync: FlightBusSyncDiagnostic;
  minersRuleFatigue: MinersRuleFatigueDiagnostic;
  cScanCadJoin: UltrasonicCScanCadDiagnostic;
  mbomLotAudit: MbomFastenerLotAuditDiagnostic;
}

/**
 * Form 700 / AFTO Form 781 Airworthiness Release Package state.
 */
export interface Form700PackageState {
  releasePackageId?: string;
  release_package_id?: string;
  tailNumber?: string;
  tail_number?: string;
  structuralStationId?: string;
  structural_station_id?: string;
  dispositionStatus?: DispositionStatus;
  disposition_status?: DispositionStatus;
  mandatedJtdTaskCard?: string;
  mandated_jtd_task_card?: string;
  hitlReviewStatus?: HitlReviewStatus;
  hitl_review_status?: HitlReviewStatus;
  stagedTurnId?: number;
  staged_turn_id?: number;
  currentTurnId?: number;
  current_turn_id?: number;
  approvedTurnId?: number | null;
  approved_turn_id?: number | null;
  reviewerRole?: string | null;
  reviewer_role?: string | null;
  approvalNotes?: string | null;
  approval_notes?: string | null;
  approvedAtUtc?: string | null;
  approved_at_utc?: string | null;
  transitionAllowed?: boolean;
  error?: string | null;
  errors?: string[];
  validation?: Form700ApprovalValidationResult;
}

export interface Form700ApprovalInput {
  releasePackageId?: string;
  release_package_id?: string;
  hitlReviewStatus?: HitlReviewStatus | string;
  hitl_review_status?: HitlReviewStatus | string;
  status?: HitlReviewStatus | string;
  stagedTurnId?: number;
  staged_turn_id?: number;
  currentTurnId?: number;
  current_turn_id?: number;
  reviewerRole?: string | null;
  reviewer_role?: string | null;
  approvalNotes?: string | null;
  approval_notes?: string | null;
  confirmationNotes?: string | null;
  confirmation_notes?: string | null;
  approvedAtUtc?: string | null;
  approved_at_utc?: string | null;
  type?: "STAGE" | "APPROVE" | "REJECT" | "CONFIRM_HITL_RELEASE" | string;
  throwOnViolation?: boolean;
}

export interface Form700ApprovalValidationResult {
  allowed: boolean;
  canApprove: boolean;
  valid: boolean;
  reason: string;
  errors: string[];
  violations: string[];
  normalizedRole: AuthorizedEngineeringRole | null;
  enforcedStandard: "MIL-HDBK-516C / DEF STAN 00-970 / SAFE-02";
}

export interface Form700ReviewStudioProps {
  packageState: Form700PackageState;
  diagnostics: AsipDiagnosticBundle;
  currentTurnId?: number;
  defaultReviewerRole?: string;
  defaultApprovalNotes?: string;
  onApproveRelease?: (nextState: Form700PackageState) => void;
  className?: string;
}

const ROLE_LOOKUP_MAP: Readonly<Record<string, AuthorizedEngineeringRole>> = {
  "lead stress engineer": "Lead Stress Engineer",
  "chief airworthiness engineer": "Chief Airworthiness Engineer",
  "structural integrity lead": "Structural Integrity Lead",
  cto: "CTO",
  "chief technical officer": "CTO",
  "chief technology officer": "CTO",
};

/**
 * Normalizes a candidate engineering role string against the authorized MIL-STD-3001 /
 * DEF STAN 00-970 airworthiness release authorities.
 */
export function normalizeAuthorizedEngineeringRole(
  roleInput?: string | null
): AuthorizedEngineeringRole | null {
  if (!roleInput || typeof roleInput !== "string") {
    return null;
  }
  const cleaned = roleInput.trim().toLowerCase();
  if (ROLE_LOOKUP_MAP[cleaned]) {
    return ROLE_LOOKUP_MAP[cleaned];
  }
  for (const [key, canonical] of Object.entries(ROLE_LOOKUP_MAP)) {
    if (cleaned.includes(key)) {
      return canonical;
    }
  }
  return null;
}

/**
 * Validates whether a Form 700 / AFTO Form 781 airworthiness release package can
 * transition from `PENDING_HITL_REVIEW` to `CONFIRMED_BY_ENGINEER` (`SAFE-02`).
 *
 * Supports both single-object `(combinedInput)` and two-argument `(packageState, request)`
 * call signatures.
 */
export function canApproveForm700Release(
  stateOrInput: Form700PackageState | Form700ApprovalInput,
  approvalRequest?: Form700ApprovalInput
): Form700ApprovalValidationResult {
  const merged: Form700ApprovalInput = {
    ...(stateOrInput ?? {}),
    ...(approvalRequest ?? {}),
  };

  const errors: string[] = [];

  const releasePackageId =
    merged.releasePackageId ?? merged.release_package_id ?? "";
  if (!releasePackageId || String(releasePackageId).trim().length === 0) {
    errors.push(
      "SAFE-02 Violation: Missing releasePackageId (expected staged package ID such as AWR-700-20261102-ZM151)."
    );
  }

  const currentStatus =
    (stateOrInput as Form700PackageState)?.hitlReviewStatus ??
    (stateOrInput as Form700PackageState)?.hitl_review_status ??
    merged.hitlReviewStatus ??
    merged.hitl_review_status ??
    merged.status ??
    "PENDING_HITL_REVIEW";

  if (currentStatus !== "PENDING_HITL_REVIEW") {
    errors.push(
      `SAFE-02 Violation: Package status must be "PENDING_HITL_REVIEW" before engineering confirmation (received "${currentStatus}").`
    );
  }

  const stagedTurnId =
    merged.stagedTurnId ??
    merged.staged_turn_id ??
    (stateOrInput as Form700PackageState)?.stagedTurnId ??
    (stateOrInput as Form700PackageState)?.staged_turn_id;

  const currentTurnId =
    approvalRequest?.currentTurnId ??
    approvalRequest?.current_turn_id ??
    merged.currentTurnId ??
    merged.current_turn_id;

  if (
    typeof stagedTurnId !== "number" ||
    !Number.isFinite(stagedTurnId) ||
    typeof currentTurnId !== "number" ||
    !Number.isFinite(currentTurnId)
  ) {
    errors.push(
      "SAFE-02 Violation: Both stagedTurnId and currentTurnId must be finite turn numbers to verify two-turn HITL separation."
    );
  } else if (currentTurnId <= stagedTurnId) {
    errors.push(
      `SAFE-02 Violation: Same-turn HITL bypass blocked (currentTurnId=${currentTurnId} <= stagedTurnId=${stagedTurnId}). Airworthiness release must be staged in Turn ${stagedTurnId} and confirmed by a human engineer in a subsequent turn (Turn >= ${stagedTurnId + 1}).`
    );
  }

  const rawRole =
    approvalRequest?.reviewerRole ??
    approvalRequest?.reviewer_role ??
    merged.reviewerRole ??
    merged.reviewer_role ??
    "";
  const normalizedRole = normalizeAuthorizedEngineeringRole(rawRole);
  if (!normalizedRole) {
    errors.push(
      `SAFE-02 Violation: Unauthorized or missing reviewerRole "${rawRole}". Sign-off authority must be one of: ${AUTHORIZED_ENGINEERING_ROLES.join(", ")}.`
    );
  }

  const rawNotes =
    approvalRequest?.approvalNotes ??
    approvalRequest?.approval_notes ??
    approvalRequest?.confirmationNotes ??
    approvalRequest?.confirmation_notes ??
    merged.approvalNotes ??
    merged.approval_notes ??
    merged.confirmationNotes ??
    merged.confirmation_notes ??
    "";
  const trimmedNotes = typeof rawNotes === "string" ? rawNotes.trim() : "";
  if (trimmedNotes.length < 5) {
    errors.push(
      "SAFE-02 Violation: Explicit engineering approval notes are required (minimum 5 characters documenting MIL-STD-3001 / JTD Task Card disposition)."
    );
  }

  const allowed = errors.length === 0;
  const reason = allowed
    ? `SAFE-02 Verified: Package ${releasePackageId} approved in Turn ${currentTurnId} (staged in Turn ${stagedTurnId}) by ${normalizedRole}.`
    : errors.join(" | ");

  return {
    allowed,
    canApprove: allowed,
    valid: allowed,
    reason,
    errors,
    violations: errors,
    normalizedRole,
    enforcedStandard: "MIL-HDBK-516C / DEF STAN 00-970 / SAFE-02",
  };
}

/**
 * Deterministic two-turn HITL state machine transition for Aircraft Form 700 / AFTO Form 781.
 *
 * - Turn 1 (`type: "STAGE"`): Stages package in `PENDING_HITL_REVIEW`.
 * - Turn 2+ (`type: "APPROVE"` / `"CONFIRM_HITL_RELEASE"`): Validates via `canApproveForm700Release`.
 *   If valid, transitions to `CONFIRMED_BY_ENGINEER`. If invalid (e.g., same-turn attempt or
 *   unauthorized role), preserves `PENDING_HITL_REVIEW` and records the violation details.
 */
export function transitionForm700State(
  currentState: Form700PackageState,
  action: Form700ApprovalInput
): Form700PackageState {
  const actionType = (action?.type ?? "APPROVE").toUpperCase();
  const basePackageId =
    currentState.releasePackageId ??
    currentState.release_package_id ??
    action.releasePackageId ??
    action.release_package_id ??
    "";
  const baseTail =
    currentState.tailNumber ?? currentState.tail_number ?? "ZM151";
  const baseStation =
    currentState.structuralStationId ??
    currentState.structural_station_id ??
    "Frame 496";
  const baseDisposition =
    currentState.dispositionStatus ??
    currentState.disposition_status ??
    "SERVICEABLE_WITH_TORQUE_RECHECK";
  const baseTaskCard =
    currentState.mandatedJtdTaskCard ??
    currentState.mandated_jtd_task_card ??
    "JTD Task Card 53-11-00-280";
  const stagedTurn =
    currentState.stagedTurnId ??
    currentState.staged_turn_id ??
    action.stagedTurnId ??
    action.staged_turn_id ??
    1;

  if (actionType === "STAGE") {
    return {
      ...currentState,
      releasePackageId: basePackageId,
      release_package_id: basePackageId,
      tailNumber: baseTail,
      tail_number: baseTail,
      structuralStationId: baseStation,
      structural_station_id: baseStation,
      dispositionStatus: baseDisposition,
      disposition_status: baseDisposition,
      mandatedJtdTaskCard: baseTaskCard,
      mandated_jtd_task_card: baseTaskCard,
      hitlReviewStatus: "PENDING_HITL_REVIEW",
      hitl_review_status: "PENDING_HITL_REVIEW",
      stagedTurnId: stagedTurn,
      staged_turn_id: stagedTurn,
      currentTurnId: stagedTurn,
      current_turn_id: stagedTurn,
      approvedTurnId: null,
      approved_turn_id: null,
      reviewerRole: null,
      reviewer_role: null,
      approvalNotes: null,
      approval_notes: null,
      transitionAllowed: true,
      error: null,
      errors: [],
    };
  }

  if (actionType === "REJECT") {
    const rawNotes =
      action.approvalNotes ??
      action.approval_notes ??
      action.confirmationNotes ??
      action.confirmation_notes ??
      "Rejected by engineering reviewer.";
    return {
      ...currentState,
      releasePackageId: basePackageId,
      release_package_id: basePackageId,
      tailNumber: baseTail,
      tail_number: baseTail,
      structuralStationId: baseStation,
      structural_station_id: baseStation,
      dispositionStatus: baseDisposition,
      disposition_status: baseDisposition,
      mandatedJtdTaskCard: baseTaskCard,
      mandated_jtd_task_card: baseTaskCard,
      hitlReviewStatus: "REJECTED_BY_ENGINEER",
      hitl_review_status: "REJECTED_BY_ENGINEER",
      stagedTurnId: stagedTurn,
      staged_turn_id: stagedTurn,
      approvalNotes: String(rawNotes).trim(),
      approval_notes: String(rawNotes).trim(),
      transitionAllowed: true,
      error: null,
      errors: [],
    };
  }

  const validation = canApproveForm700Release(currentState, action);
  if (!validation.allowed) {
    if (action?.throwOnViolation) {
      throw new Error(validation.reason);
    }
    const existingStatus =
      currentState.hitlReviewStatus ??
      currentState.hitl_review_status ??
      "PENDING_HITL_REVIEW";
    return {
      ...currentState,
      releasePackageId: basePackageId,
      release_package_id: basePackageId,
      tailNumber: baseTail,
      tail_number: baseTail,
      structuralStationId: baseStation,
      structural_station_id: baseStation,
      dispositionStatus: baseDisposition,
      disposition_status: baseDisposition,
      mandatedJtdTaskCard: baseTaskCard,
      mandated_jtd_task_card: baseTaskCard,
      hitlReviewStatus: existingStatus,
      hitl_review_status: existingStatus,
      stagedTurnId: stagedTurn,
      staged_turn_id: stagedTurn,
      currentTurnId:
        action.currentTurnId ?? action.current_turn_id ?? stagedTurn,
      current_turn_id:
        action.currentTurnId ?? action.current_turn_id ?? stagedTurn,
      transitionAllowed: false,
      error: validation.reason,
      errors: validation.errors,
      validation,
    };
  }

  const approvedTurn =
    action.currentTurnId ?? action.current_turn_id ?? stagedTurn + 1;
  const approvedNotes = String(
    action.approvalNotes ??
      action.approval_notes ??
      action.confirmationNotes ??
      action.confirmation_notes ??
      ""
  ).trim();
  const approvedTimestamp =
    action.approvedAtUtc ??
    action.approved_at_utc ??
    currentState.approvedAtUtc ??
    currentState.approved_at_utc ??
    null;

  return {
    ...currentState,
    releasePackageId: basePackageId,
    release_package_id: basePackageId,
    tailNumber: baseTail,
    tail_number: baseTail,
    structuralStationId: baseStation,
    structural_station_id: baseStation,
    dispositionStatus: baseDisposition,
    disposition_status: baseDisposition,
    mandatedJtdTaskCard: baseTaskCard,
    mandated_jtd_task_card: baseTaskCard,
    hitlReviewStatus: "CONFIRMED_BY_ENGINEER",
    hitl_review_status: "CONFIRMED_BY_ENGINEER",
    stagedTurnId: stagedTurn,
    staged_turn_id: stagedTurn,
    currentTurnId: approvedTurn,
    current_turn_id: approvedTurn,
    approvedTurnId: approvedTurn,
    approved_turn_id: approvedTurn,
    reviewerRole: validation.normalizedRole,
    reviewer_role: validation.normalizedRole,
    approvalNotes: approvedNotes,
    approval_notes: approvedNotes,
    approvedAtUtc: approvedTimestamp,
    approved_at_utc: approvedTimestamp,
    transitionAllowed: true,
    error: null,
    errors: [],
    validation,
  };
}

/**
 * CSS styles implementing the 4-way ASIP diagnostic cards and Modern Web Guidance
 * `validate-input-after-interaction` rules:
 * - Static hints/rules placed ABOVE inputs so browser autocomplete/mobile keyboards do not obscure them.
 * - `:user-invalid` and `:user-valid` pseudo-classes for post-interaction validation feedback.
 * - `.field:has(input:user-invalid, select:user-invalid, textarea:user-invalid) .rules-list` highlighting.
 */
export const FORM700_REVIEW_STUDIO_STYLES = `
.f35-form700-studio {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  color: #0f172a;
}

.f35-form700-header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
  border-radius: 0.5rem;
  background: #0f172a;
  color: #f8fafc;
}

.f35-status-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.35rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.f35-status-badge[data-status="PENDING_HITL_REVIEW"] {
  background: #fef3c7;
  color: #92400e;
  border: 1px solid #f59e0b;
}

.f35-status-badge[data-status="CONFIRMED_BY_ENGINEER"] {
  background: #dcfce7;
  color: #166534;
  border: 1px solid #22c55e;
}

.f35-status-badge[data-status="REJECTED_BY_ENGINEER"] {
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #ef4444;
}

.f35-asip-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1rem;
}

.f35-asip-card {
  border: 1px solid #cbd5e1;
  border-radius: 0.5rem;
  padding: 1rem;
  background: #ffffff;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
}

.f35-asip-card h4 {
  margin: 0 0 0.5rem 0;
  font-size: 0.95rem;
  color: #0f172a;
}

.f35-asip-dl {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 0.35rem 0.75rem;
  margin: 0;
  font-size: 0.85rem;
}

.f35-asip-dl dt {
  color: #475569;
  font-weight: 500;
}

.f35-asip-dl dd {
  margin: 0;
  font-weight: 600;
  color: #0f172a;
  text-align: right;
}

.f35-hitl-form {
  border: 1px solid #cbd5e1;
  border-radius: 0.5rem;
  padding: 1.25rem;
  background: #f8fafc;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin-block-end: 1rem;
}

.field label {
  font-weight: 600;
  font-size: 0.9rem;
  color: #0f172a;
}

.rules-list {
  margin: 0;
  padding-inline-start: 1.25rem;
  font-size: 0.8rem;
  color: #475569;
}

.field input,
.field select,
.field textarea {
  padding: 0.55rem 0.75rem;
  border: 1px solid #94a3b8;
  border-radius: 0.375rem;
  font-size: 0.9rem;
  background: #ffffff;
  color: #0f172a;
}

.field input:user-invalid,
.field select:user-invalid,
.field textarea:user-invalid {
  border-color: #d93025;
  outline-color: #d93025;
}

.field input:user-valid,
.field select:user-valid,
.field textarea:user-valid {
  border-color: #188038;
}

.field:has(input:user-invalid, select:user-invalid, textarea:user-invalid) .rules-list {
  color: #d93025;
  font-weight: 600;
}

.error-msg {
  color: #d93025;
  font-size: 0.82rem;
  font-weight: 600;
  margin: 0;
}
`.trim();

/**
 * Form700ReviewStudio — Renders the 4-way ASIP diagnostic cards and the guardrailed
 * two-turn HITL Aircraft Form 700 / AFTO Form 781 engineering sign-off studio (`SAFE-01`, `SAFE-02`).
 *
 * Strictly renders values passed via props without inventing or recalculating any numbers.
 */
export function Form700ReviewStudio(props: Form700ReviewStudioProps): VNode {
  const {
    packageState,
    diagnostics,
    currentTurnId,
    defaultReviewerRole = "",
    defaultApprovalNotes = "",
    className,
  } = props;

  const releasePackageId =
    packageState.releasePackageId ?? packageState.release_package_id ?? "";
  const tailNumber =
    packageState.tailNumber ?? packageState.tail_number ?? "";
  const stationId =
    packageState.structuralStationId ??
    packageState.structural_station_id ??
    "";
  const dispositionStatus =
    packageState.dispositionStatus ?? packageState.disposition_status ?? "";
  const mandatedTaskCard =
    packageState.mandatedJtdTaskCard ??
    packageState.mandated_jtd_task_card ??
    "";
  const hitlStatus: HitlReviewStatus =
    packageState.hitlReviewStatus ??
    packageState.hitl_review_status ??
    "PENDING_HITL_REVIEW";
  const stagedTurnId =
    packageState.stagedTurnId ?? packageState.staged_turn_id ?? 1;
  const effectiveCurrentTurnId =
    currentTurnId ??
    packageState.currentTurnId ??
    packageState.current_turn_id ??
    stagedTurnId;

  // Card 1 props (1553 Flight Bus Sync)
  const bus = diagnostics?.flightBusSync ?? {};
  const exceedanceEventId =
    bus.exceedanceEventId ?? bus.exceedance_event_id ?? "";
  const peakGLoad = bus.peakGLoad ?? bus.peak_g_load;
  const machNumber = bus.machNumber ?? bus.mach_number;
  const egtCelsius = bus.egtCelsius ?? bus.egt_celsius;
  const timestampUtc = bus.timestampUtc ?? bus.timestamp_utc ?? "";
  const durationSeconds = bus.durationSeconds ?? bus.duration_seconds;
  const busStationId =
    bus.structuralStationId ?? bus.structural_station_id ?? stationId;

  // Card 2 props (Palmgren-Miner & Rainflow Math)
  const fatigue = diagnostics?.minersRuleFatigue ?? {};
  const minersDamageDelta =
    fatigue.minersRuleDamageDelta ??
    fatigue.miners_rule_damage_delta ??
    fatigue.cumulativeDamageIndex ??
    fatigue.cumulative_damage_index;
  const calculatedYieldPct =
    fatigue.calculatedYieldPct ?? fatigue.calculated_yield_pct;
  const yieldLimitPct = fatigue.yieldLimitPct ?? fatigue.yield_limit_pct;
  const requiredNdiAction =
    fatigue.requiredNdiAction ?? fatigue.required_ndi_action ?? "";
  const triggeredJtdRule =
    fatigue.triggeredJtdRule ?? fatigue.triggered_jtd_rule ?? "";
  const fatigueRefDoc =
    fatigue.referenceDocId ?? fatigue.reference_doc_id ?? "DOC-04";

  // Card 3 props (Multimodal Ultrasonic C-Scan & 3D CAD Join)
  const cscan = diagnostics?.cScanCadJoin ?? {};
  const cScanDocId =
    cscan.cScanDocumentId ?? cscan.c_scan_document_id ?? "DOC-06";
  const cadRefDocId =
    cscan.cadReferenceDocumentId ?? cscan.cad_reference_document_id ?? "DOC-05";
  const srmChapter = cscan.srmChapter ?? cscan.srm_chapter ?? "SRM 51-40";
  const cscanStation =
    cscan.structuralStation ?? cscan.structural_station ?? stationId;
  const fastenerHoleId = cscan.fastenerHoleId ?? cscan.fastener_hole_id ?? "";
  const measuredElongationIn =
    cscan.measuredShearElongationIn ?? cscan.measured_shear_elongation_in;
  const allowableElongationIn =
    cscan.allowableElongationLimitIn ?? cscan.allowable_elongation_limit_in;

  // Card 4 props (As-Maintained mBOM Fastener Lot Audit)
  const mbom = diagnostics?.mbomLotAudit ?? {};
  const mbomRecordId = mbom.mbomRecordId ?? mbom.mbom_record_id ?? "";
  const materialAlloy = mbom.materialAlloy ?? mbom.material_alloy ?? "";
  const fastenerLotNumber =
    mbom.fastenerLotNumber ?? mbom.fastener_lot_number ?? "";
  const hoursSinceInstall =
    mbom.hoursSinceInstall ?? mbom.hours_since_install;
  const mbomAllowableLimitIn =
    mbom.allowableLimitIn ?? mbom.allowable_limit_in ?? allowableElongationIn;
  const globalFleetAffectedTailsCount =
    mbom.globalFleetAffectedTailsCount ??
    mbom.global_fleet_affected_tails_count;
  const inspectionWindowDays =
    mbom.inspectionWindowDays ?? mbom.inspection_window_days ?? 30;

  const isSameTurnBlocked = effectiveCurrentTurnId <= stagedTurnId;
  const validationPreview = canApproveForm700Release(packageState, {
    currentTurnId: effectiveCurrentTurnId,
    reviewerRole: packageState.reviewerRole ?? defaultReviewerRole,
    approvalNotes: packageState.approvalNotes ?? defaultApprovalNotes,
  });

  const handleFieldValidationSync = (event: { currentTarget?: { validity?: { valid: boolean }; setAttribute?: (name: string, val: string) => void } }) => {
    const target = event?.currentTarget;
    if (target && target.validity && typeof target.setAttribute === "function") {
      target.setAttribute("aria-invalid", String(!target.validity.valid));
    }
  };

  return (
    <section
      className={
        className
          ? `f35-form700-studio ${className}`
          : "f35-form700-studio"
      }
      aria-labelledby="f35-form700-studio-heading"
      data-component="Form700ReviewStudio"
      data-release-package-id={releasePackageId}
      data-hitl-status={hitlStatus}
      data-staged-turn-id={String(stagedTurnId)}
      data-current-turn-id={String(effectiveCurrentTurnId)}
    >
      <style>{FORM700_REVIEW_STUDIO_STYLES}</style>

      <header className="f35-form700-header">
        <div>
          <h3 id="f35-form700-studio-heading" style={{ margin: 0 }}>
            MIL-STD-3001 Structural Appraisal Report &amp; Aircraft Form 700 / AFTO Form 781
          </h3>
          <p style={{ margin: "0.25rem 0 0 0", fontSize: "0.85rem", opacity: 0.9 }}>
            Package ID: <strong>{releasePackageId}</strong> · Tail:{" "}
            <strong>{tailNumber}</strong> · Station:{" "}
            <strong>{stationId}</strong> · Disposition:{" "}
            <strong>{dispositionStatus}</strong> · Mandated Task Card:{" "}
            <strong>{mandatedTaskCard}</strong>
          </p>
        </div>
        <span
          className="f35-status-badge"
          data-status={hitlStatus}
          role="status"
          aria-live="polite"
        >
          {hitlStatus}
        </span>
      </header>

      <div
        className="f35-asip-grid"
        role="region"
        aria-label="4-Way ASIP Structural Appraisal Diagnostic Cards"
      >
        {/* Card 1: 1553 Flight Bus Sync */}
        <article
          className="f35-asip-card"
          data-card="1553-flight-bus-sync"
          aria-labelledby="asip-card-1-title"
        >
          <h4 id="asip-card-1-title">1. 1553 Flight Bus Sync</h4>
          <dl className="f35-asip-dl">
            <dt>Exceedance Event ID</dt>
            <dd>{exceedanceEventId}</dd>
            <dt>Peak Normal Load</dt>
            <dd>
              {peakGLoad !== undefined ? `${peakGLoad} G` : ""}
              {machNumber !== undefined ? ` at Mach ${machNumber}` : ""}
            </dd>
            <dt>Thermal / EGT</dt>
            <dd>
              {egtCelsius !== undefined
                ? `${Number(egtCelsius).toFixed(1)}°C EGT`
                : ""}
            </dd>
            <dt>Event Timestamp (UTC)</dt>
            <dd>{timestampUtc}</dd>
            <dt>Exceedance Window</dt>
            <dd>
              {durationSeconds !== undefined ? `${durationSeconds}s window` : ""}{" "}
              on {busStationId}
            </dd>
          </dl>
        </article>

        {/* Card 2: Deterministic Palmgren-Miner & Rainflow Math */}
        <article
          className="f35-asip-card"
          data-card="palmgren-miner-rainflow"
          aria-labelledby="asip-card-2-title"
        >
          <h4 id="asip-card-2-title">
            2. Deterministic Palmgren-Miner &amp; Rainflow Math
          </h4>
          <dl className="f35-asip-dl">
            <dt>Cumulative Damage (D = ∑ nᵢ / Nᵢ)</dt>
            <dd>{minersDamageDelta !== undefined ? String(minersDamageDelta) : ""}</dd>
            <dt>Calculated Yield vs Limit</dt>
            <dd>
              {calculatedYieldPct !== undefined ? `${calculatedYieldPct}%` : ""}{" "}
              yield &gt;{" "}
              {yieldLimitPct !== undefined ? `${yieldLimitPct}%` : "100%"} limit
            </dd>
            <dt>Mandated NDI Action</dt>
            <dd>{requiredNdiAction}</dd>
            <dt>Governing JTD Rule</dt>
            <dd>
              {triggeredJtdRule} ({fatigueRefDoc})
            </dd>
          </dl>
        </article>

        {/* Card 3: Multimodal Ultrasonic C-Scan & 3D CAD Join */}
        <article
          className="f35-asip-card"
          data-card="ultrasonic-cscan-cad-join"
          aria-labelledby="asip-card-3-title"
        >
          <h4 id="asip-card-3-title">
            3. Multimodal Ultrasonic C-Scan ({cScanDocId}) &amp; 3D CAD Join ({cadRefDocId} {srmChapter})
          </h4>
          <dl className="f35-asip-dl">
            <dt>Localized Feature</dt>
            <dd>
              {cscanStation} — {fastenerHoleId}
            </dd>
            <dt>Shear Elongation vs Limit</dt>
            <dd>
              {measuredElongationIn !== undefined
                ? `${measuredElongationIn} in`
                : ""}{" "}
              shear elongation vs{" "}
              {allowableElongationIn !== undefined
                ? `${allowableElongationIn} in`
                : ""}{" "}
              limit
            </dd>
            <dt>Source Artifacts</dt>
            <dd>
              {cScanDocId} joined with {cadRefDocId} ({srmChapter})
            </dd>
          </dl>
        </article>

        {/* Card 4: As-Maintained mBOM Fastener Lot Audit */}
        <article
          className="f35-asip-card"
          data-card="mbom-fastener-lot-audit"
          aria-labelledby="asip-card-4-title"
        >
          <h4 id="asip-card-4-title">
            4. As-Maintained mBOM Fastener Lot Audit
          </h4>
          <dl className="f35-asip-dl">
            <dt>mBOM Record ID</dt>
            <dd>{mbomRecordId}</dd>
            <dt>Alloy &amp; Lot Number</dt>
            <dd>
              {materialAlloy}, {fastenerLotNumber}
            </dd>
            <dt>Service Time &amp; Limit</dt>
            <dd>
              {hoursSinceInstall !== undefined
                ? `${Number(hoursSinceInstall).toFixed(1)} hrs since install`
                : ""}
              {mbomAllowableLimitIn !== undefined
                ? ` (limit ${mbomAllowableLimitIn} in)`
                : ""}
            </dd>
            <dt>Fleet-Wide Lot Impact</dt>
            <dd>
              {globalFleetAffectedTailsCount !== undefined
                ? `${globalFleetAffectedTailsCount} global fleet tails affected for ${inspectionWindowDays}-day proactive inspection`
                : ""}
            </dd>
          </dl>
        </article>
      </div>

      {/* Two-Turn HITL Engineering Sign-Off Gate (SAFE-02 + Modern Web Guidance validate-input-after-interaction) */}
      <form
        className="f35-hitl-form"
        aria-label="Form 700 HITL Engineering Release Sign-Off"
        data-turn-gate={isSameTurnBlocked ? "LOCKED_SAME_TURN" : "UNLOCKED_NEXT_TURN"}
        noValidate={false}
      >
        <h4 style={{ marginTop: 0, marginBottom: "0.75rem" }}>
          Human-in-the-Loop (HITL) Airworthiness Release Gate (SAFE-02)
        </h4>

        <div className="field">
          <label htmlFor="form700-reviewer-role">
            Authorized Engineering Release Authority
          </label>
          <ul id="form700-role-rules" className="rules-list">
            <li>
              Must be signed by an authorized MIL-STD-3001 / DEF STAN 00-970 role:{" "}
              {AUTHORIZED_ENGINEERING_ROLES.join(", ")}.
            </li>
            <li>
              Two-Turn Gate: Staged in Turn {stagedTurnId}; current session is Turn{" "}
              {effectiveCurrentTurnId}.
            </li>
          </ul>
          <select
            id="form700-reviewer-role"
            name="reviewerRole"
            required={true}
            defaultValue={packageState.reviewerRole ?? defaultReviewerRole}
            aria-describedby="form700-role-rules"
            aria-errormessage="form700-role-error"
            aria-invalid="false"
            onBlur={handleFieldValidationSync}
            onChange={handleFieldValidationSync}
          >
            <option value="">Select authorized engineering role...</option>
            {AUTHORIZED_ENGINEERING_ROLES.map((role) => (
              <option key={role} value={role}>
                {role}
              </option>
            ))}
          </select>
          <p
            id="form700-role-error"
            className="error-msg"
            aria-live="polite"
            hidden={validationPreview.normalizedRole !== null}
          >
            {validationPreview.normalizedRole === null
              ? "Select an authorized engineering authority (Lead Stress Engineer, Chief Airworthiness Engineer, Structural Integrity Lead, or CTO)."
              : ""}
          </p>
        </div>

        <div className="field">
          <label htmlFor="form700-approval-notes">
            Engineering Disposition &amp; Torque-Recheck Sign-Off Notes
          </label>
          <ul id="form700-notes-rules" className="rules-list">
            <li>
              Enter explicit engineering sign-off notes referencing{" "}
              <strong>{mandatedTaskCard}</strong> and disposition{" "}
              <strong>{dispositionStatus}</strong> (minimum 5 characters).
            </li>
          </ul>
          <textarea
            id="form700-approval-notes"
            name="approvalNotes"
            required={true}
            minLength={5}
            rows={3}
            defaultValue={packageState.approvalNotes ?? defaultApprovalNotes}
            aria-describedby="form700-notes-rules"
            aria-errormessage="form700-notes-error"
            aria-invalid="false"
            onBlur={handleFieldValidationSync}
            onInput={handleFieldValidationSync}
          />
          <p
            id="form700-notes-error"
            className="error-msg"
            aria-live="polite"
            hidden={validationPreview.allowed}
          >
            {!validationPreview.allowed ? validationPreview.reason : ""}
          </p>
        </div>

        <button
          type="submit"
          disabled={isSameTurnBlocked || hitlStatus === "CONFIRMED_BY_ENGINEER"}
          aria-disabled={
            isSameTurnBlocked || hitlStatus === "CONFIRMED_BY_ENGINEER"
          }
          data-action="confirm-form700-hitl-release"
        >
          {hitlStatus === "CONFIRMED_BY_ENGINEER"
            ? "Form 700 Release Confirmed by Engineer"
            : isSameTurnBlocked
              ? `Locked in Turn ${stagedTurnId} (Requires Turn >= ${stagedTurnId + 1} HITL Sign-Off)`
              : "Approve & Sign Form 700 Airworthiness Release"}
        </button>
      </form>
    </section>
  );
}

export default Form700ReviewStudio;
