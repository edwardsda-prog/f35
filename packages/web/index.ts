/**
 * @fileoverview Public entrypoint for `@f35-sustainment-agent/web` (`packages/web`).
 *
 * Exports:
 * 0. UC 0 / UC 0.1 / UC 0.5 Maintenance Data & Multi-Table Spreadsheet Card (`MaintenanceSheetCard`,
 *    `formatStatusBadge`, `formatFaultSeverityBadge`, `formatCndFlagBadge`,
 *    `formatToolCalibrationBadge`, `formatBayDispatchBadge`, `resolveStatusBadgeTone`,
 *    `resolveReferencedTables`, `MAINTENANCE_STATUS_BADGES`, `AIRCRAFT_STATUS_BADGES`,
 *    `FAULT_SEVERITY_BADGES`, `CND_FLAG_BADGES`, `TOOL_CALIBRATION_STATUS_BADGES`,
 *    `BAY_DISPATCH_STATUS_BADGES`, `F35_WAREHOUSE_TABLES`, `F35_WAREHOUSE_TABLE_BADGES`,
 *    `STATUS_BADGE_FIELD_NAMES`, `MAINTENANCE_SHEET_CARD_STYLES`).
 * 1. UC1 Supply & Readiness Analytics Canvas (`VegaCanvas`, `validateVegaLiteSpec`,
 *    `extractVegaLiteBlocks`, `renderMarkdownFallbackTable`, `formatDualCompatibleVegaOutput`,
 *    `VEGA_LITE_V5_SCHEMA_URL`).
 * 2. UC3 MIL-STD-3001 Structural Appraisal Report & Aircraft Form 700 HITL Review Studio
 *    (`Form700ReviewStudio`, `canApproveForm700Release`, `transitionForm700State`,
 *    `normalizeAuthorizedEngineeringRole`, `AUTHORIZED_ENGINEERING_ROLES`).
 * 3. Isomorphic VNode-to-HTML serializer (`renderVNodeToHtml`) for SSR and deterministic verification.
 */

export {
  F35_WAREHOUSE_TABLES,
  F35_WAREHOUSE_TABLE_BADGES,
  AIRCRAFT_STATUS_BADGES,
  FAULT_SEVERITY_BADGES,
  CND_FLAG_BADGES,
  TOOL_CALIBRATION_STATUS_BADGES,
  BAY_DISPATCH_STATUS_BADGES,
  MAINTENANCE_STATUS_BADGES,
  STATUS_BADGE_FIELD_NAMES,
  MAINTENANCE_SHEET_CARD_STYLES,
  formatFaultSeverityBadge,
  formatCndFlagBadge,
  formatToolCalibrationBadge,
  formatBayDispatchBadge,
  formatStatusBadge,
  resolveStatusBadgeTone,
  resolveReferencedTables,
  MaintenanceSheetCard,
} from "./components/MaintenanceSheetCard";

export type {
  F35WarehouseTableName,
  WarehouseTableBadgeMeta,
  StatusBadgeTone,
  SpreadsheetColumnHeader,
  SpreadsheetFormulaFooter,
  MaintenanceSpreadsheetCardProps,
  MaintenanceSpreadsheetCard,
} from "./components/MaintenanceSheetCard";

export {
  VEGA_LITE_V5_SCHEMA,
  VEGA_LITE_V5_SCHEMA_URL,
  SUPPORTED_UC1_CHART_KINDS,
  SUPPORTED_UC1_CHART_IDS,
  VEGA_CANVAS_RESPONSIVE_TABLE_CSS,
  VEGA_CANVAS_RESPONSIVE_TABLE_STYLES,
  React,
  validateVegaLiteSpec,
  extractVegaLiteBlocks,
  renderMarkdownFallbackTable,
  formatDualCompatibleVegaOutput,
  VegaCanvas,
} from "./components/VegaCanvas";

export type {
  VNodeElement,
  VNode,
  VNodeChild,
  SupportedUc1ChartKind,
  SupportedUc1ChartId,
  VegaLiteV5Spec,
  ActuatorSummaryTableRow,
  ActuatorFleetFallbackRow,
  SupplyReplenishmentRecommendation,
  VegaValidationResult,
  VegaLiteValidationResult,
  VegaCanvasProps,
} from "./components/VegaCanvas";

export {
  AUTHORIZED_ENGINEERING_ROLES,
  FORM700_REVIEW_STUDIO_STYLES,
  normalizeAuthorizedEngineeringRole,
  canApproveForm700Release,
  transitionForm700State,
  Form700ReviewStudio,
} from "./components/Form700ReviewStudio";

export type {
  HitlReviewStatus,
  DispositionStatus,
  AuthorizedEngineeringRole,
  FlightBusSyncDiagnostic,
  MinersRuleFatigueDiagnostic,
  UltrasonicCScanCadDiagnostic,
  MbomFastenerLotAuditDiagnostic,
  AsipDiagnosticBundle,
  Form700PackageState,
  Form700ApprovalInput,
  Form700ApprovalValidationResult,
  Form700ReviewStudioProps,
} from "./components/Form700ReviewStudio";

import type { VNode, VNodeChild } from "./components/VegaCanvas";

const VOID_HTML_ELEMENTS = new Set([
  "area",
  "base",
  "br",
  "col",
  "embed",
  "hr",
  "img",
  "input",
  "link",
  "meta",
  "param",
  "source",
  "track",
  "wbr",
]);

function escapeHtmlText(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function serializeStyleObject(styleObj: Record<string, unknown>): string {
  return Object.entries(styleObj)
    .filter(([, val]) => val !== undefined && val !== null)
    .map(([key, val]) => {
      const kebabKey = key.replace(/[A-Z]/g, (m) => `-${m.toLowerCase()}`);
      return `${kebabKey}:${String(val)}`;
    })
    .join(";");
}

/**
 * Serializes a `VNode` tree produced by `VegaCanvas`, `MaintenanceSheetCard`, or `Form700ReviewStudio` into
 * deterministic HTML for SSR rendering and verification assertions.
 */
export function renderVNodeToHtml(node: VNodeChild): string {
  if (node === null || node === undefined || typeof node === "boolean") {
    return "";
  }
  if (typeof node === "string" || typeof node === "number") {
    return escapeHtmlText(String(node));
  }
  if (Array.isArray(node)) {
    return node.map((child) => renderVNodeToHtml(child)).join("");
  }

  const vnode = node as VNode;
  if (typeof vnode.type === "function") {
    return renderVNodeToHtml(
      vnode.type({ ...(vnode.props ?? {}) }) as VNodeChild
    );
  }

  const tag = String(vnode.type);
  const attrs: string[] = [];

  for (const [rawKey, val] of Object.entries(vnode.props ?? {})) {
    if (
      rawKey === "children" ||
      rawKey === "key" ||
      typeof val === "function" ||
      val === undefined ||
      val === null ||
      val === false
    ) {
      continue;
    }
    const attrName =
      rawKey === "className"
        ? "class"
        : rawKey === "htmlFor"
          ? "for"
          : rawKey === "tabIndex"
            ? "tabindex"
            : rawKey === "minLength"
              ? "minlength"
              : rawKey === "defaultValue"
                ? "value"
                : rawKey;

    if (rawKey === "style" && typeof val === "object") {
      const styleStr = serializeStyleObject(val as Record<string, unknown>);
      if (styleStr) {
        attrs.push(`style="${escapeHtmlText(styleStr)}"`);
      }
      continue;
    }

    if (val === true) {
      attrs.push(attrName);
    } else {
      attrs.push(`${attrName}="${escapeHtmlText(String(val))}"`);
    }
  }

  const attrString = attrs.length > 0 ? ` ${attrs.join(" ")}` : "";
  if (VOID_HTML_ELEMENTS.has(tag)) {
    return `<${tag}${attrString}/>`;
  }

  const rawChildren = vnode.props?.children;
  const childArray: VNodeChild[] = Array.isArray(rawChildren)
    ? (rawChildren as VNodeChild[])
    : rawChildren !== undefined && rawChildren !== null
      ? [rawChildren as VNodeChild]
      : [];

  const childrenHtml =
    tag === "style" || tag === "script"
      ? childArray.map((c: VNodeChild) => String(c ?? "")).join("")
      : childArray.map((c: VNodeChild) => renderVNodeToHtml(c)).join("");

  return `<${tag}${attrString}>${childrenHtml}</${tag}>`;
}
