/**
 * @fileoverview Vega-Lite v5 Canvas & Dual-Compatible Markdown Fallback Table Component (UC1)
 *
 * Conforms strictly to `/packages/web/AGENTS.md` and `SA_F35.md` Section 3:
 * 1. Validates inline Vega-Lite v5 JSON chart specifications against
 *    `https://vega.github.io/schema/vega-lite/v5.json`.
 * 2. Renders UC1 visual specifications:
 *    - `depot_stock_vs_demand_bar_chart`: Grouped Bar Chart comparing Regional Depot Stock
 *      vs 30-Day Projected Squadron Demand across RAF Marham (`DEP-UK-01`) and
 *      HMS Queen Elizabeth (`DEP-UK-02`).
 *    - `actuator_fatigue_threshold_chart`: Threshold Line/Bar Chart comparing airframe
 *      horizontal tail actuator flight hours (`ZM151`, `ZM154`) against the mandatory
 *      life-limit condemnation threshold (`1,000.0` hrs).
 * 3. Renders dual-compatible outputs: both a code-fenced ```vega-lite JSON specification
 *    and a formatted Markdown / accessible HTML fallback data table (`Tail Number`,
 *    `Part S/N`, `Current Hours`, `Limit Hours`, `Variance`, `Depot Stock`,
 *    `Readiness Status`, `Assigned Sortie`).
 * 4. Strictly renders values passed via props from agent responses and NEVER invents
 *    or recalculates supply, telemetry, or structural figures (`SAFE-01`).
 */

export const VEGA_LITE_V5_SCHEMA = "https://vega.github.io/schema/vega-lite/v5.json" as const;
export const VEGA_LITE_V5_SCHEMA_URL = VEGA_LITE_V5_SCHEMA;

export const SUPPORTED_UC1_CHART_KINDS = [
  "depot_stock_vs_demand_bar_chart",
  "actuator_fatigue_threshold_chart",
] as const;
export const SUPPORTED_UC1_CHART_IDS = SUPPORTED_UC1_CHART_KINDS;

export type SupportedUc1ChartKind = (typeof SUPPORTED_UC1_CHART_KINDS)[number];
export type SupportedUc1ChartId = SupportedUc1ChartKind;

export type VegaLiteMarkType =
  | "bar"
  | "line"
  | "rule"
  | "point"
  | "circle"
  | "square"
  | "tick"
  | "area"
  | "rect"
  | "text";

export interface VegaLiteMarkObject {
  type: VegaLiteMarkType | string;
  color?: string;
  strokeDash?: number[];
  strokeWidth?: number;
  size?: number;
  opacity?: number;
  tooltip?: boolean | Record<string, unknown>;
  cornerRadiusEnd?: number;
  [key: string]: unknown;
}

export type VegaLiteMark = VegaLiteMarkType | string | VegaLiteMarkObject;

export interface VegaLiteFieldDef {
  field?: string;
  type?: "quantitative" | "nominal" | "ordinal" | "temporal" | string;
  title?: string;
  datum?: string | number | boolean;
  value?: string | number | boolean;
  axis?: Record<string, unknown>;
  scale?: Record<string, unknown>;
  legend?: Record<string, unknown> | null;
  sort?: string | string[] | Record<string, unknown> | null;
  aggregate?: string;
  format?: string;
  condition?: Record<string, unknown> | Array<Record<string, unknown>>;
  [key: string]: unknown;
}

export interface VegaLiteEncoding {
  x?: VegaLiteFieldDef;
  y?: VegaLiteFieldDef;
  x2?: VegaLiteFieldDef;
  y2?: VegaLiteFieldDef;
  xOffset?: VegaLiteFieldDef;
  yOffset?: VegaLiteFieldDef;
  color?: VegaLiteFieldDef;
  strokeDash?: VegaLiteFieldDef;
  size?: VegaLiteFieldDef;
  shape?: VegaLiteFieldDef;
  text?: VegaLiteFieldDef;
  tooltip?: VegaLiteFieldDef | VegaLiteFieldDef[];
  [key: string]: VegaLiteFieldDef | VegaLiteFieldDef[] | undefined;
}

export interface VegaLiteLayerSpec {
  name?: string;
  title?: string;
  description?: string;
  data?: {
    values?: Array<Record<string, unknown>>;
    name?: string;
  };
  mark: VegaLiteMark;
  encoding?: VegaLiteEncoding;
  transform?: Array<Record<string, unknown>>;
}

export interface VegaLiteTitleObject {
  text: string;
  subtitle?: string | string[];
  anchor?: "start" | "middle" | "end";
  [key: string]: unknown;
}

export interface VegaLiteV5Spec {
  $schema: string;
  name?: string;
  title?: string | VegaLiteTitleObject;
  description?: string;
  width?: number | "container";
  height?: number;
  data: {
    values: Array<Record<string, unknown>>;
    name?: string;
  };
  mark?: VegaLiteMark;
  encoding?: VegaLiteEncoding;
  layer?: VegaLiteLayerSpec[];
  transform?: Array<Record<string, unknown>>;
  config?: Record<string, unknown>;
  [key: string]: unknown;
}

export interface VegaValidationResult {
  valid: boolean;
  errors: string[];
  schemaVersion: string | null;
  chartKind: SupportedUc1ChartKind | "generic_vega_lite_v5" | "invalid";
  rowCount: number;
  titleText: string | null;
}

export type VegaLiteValidationResult = VegaValidationResult;

/**
 * Dual-compatible summary row representing UC1 joined telemetry, depot stock, and sortie state.
 * Supports both camelCase (UI props) and snake_case (BigQuery / Python tool dictionary payloads)
 * without mutating or recalculating any numerical values.
 */
export interface ActuatorSummaryTableRow {
  // CamelCase props
  tailNumber?: string;
  partSerialNumber?: string;
  currentHours?: number | string;
  limitHours?: number | string;
  variance?: number | string;
  depotStock?: number | string;
  readinessStatus?: string;
  assignedSortie?: string;
  // Snake_case BigQuery / ADK tool fields
  tail_number?: string;
  part_serial_number?: string;
  part_sn?: string;
  current_flight_hours?: number | string;
  life_limit_threshold_hrs?: number | string;
  variance_hrs?: number | string;
  hours_variance?: number | string;
  depot_stock_on_hand?: number | string;
  quantity_on_hand?: number | string;
  readiness_status?: string;
  aircraft_status?: string;
  assigned_sortie?: string;
  sortie_id?: string;
}

export type ActuatorFleetFallbackRow = ActuatorSummaryTableRow;

export interface SupplyReplenishmentRecommendation {
  nsn: string;
  partName?: string;
  depotId?: string;
  depotName?: string;
  quantityOnHand: number | string;
  quantityReserved30d: number | string;
  reorderPointThreshold?: number | string;
  avgShippingEtaHours: number | string;
  sortieId?: string;
  primaryTail?: string;
  spareTail?: string;
  assignedPilotCallsign?: string;
  scheduledDepartureUtc?: string;
  sortieReadinessStatus?: string;
}

export interface VegaCanvasProps {
  /** Single Vega-Lite v5 specification to validate and render. */
  spec?: VegaLiteV5Spec;
  /** Named map or array of Vega-Lite v5 specifications (e.g., UC1 chart pair). */
  specs?: VegaLiteV5Spec[] | Record<string, VegaLiteV5Spec>;
  /** Explicit prop for UC1 Chart 1: Regional Depot Stock vs 30-Day Demand Grouped Bar Chart. */
  depotStockVsDemandChart?: VegaLiteV5Spec;
  /** Explicit prop for UC1 Chart 2: Actuator Flight Hours vs 1,000-Hr Condemnation Threshold Chart. */
  actuatorFatigueThresholdChart?: VegaLiteV5Spec;
  /** Optional raw Markdown string from the ADK agent containing ```vega-lite fenced blocks. */
  agentResponseMarkdown?: string;
  /** Structured rows for the dual-compatible Markdown & accessible HTML fallback table. */
  summaryRows: ActuatorSummaryTableRow[];
  /** Optional supply alert & tail-swap recommendation banner data from UC1 tool output. */
  supplyRecommendation?: SupplyReplenishmentRecommendation;
  /** Accessible caption ID for the responsive table region. */
  tableCaptionId?: string;
  /** Accessible table caption text. */
  tableCaption?: string;
  /** Whether to display the fenced ```vega-lite JSON source alongside the visual chart. */
  showVegaLiteSource?: boolean;
}

// ---------------------------------------------------------------------------
// Isomorphic JSX / React Element Runtime (Zero external dependency fallback)
// ---------------------------------------------------------------------------

export interface VNodeElement {
  $$typeof: symbol;
  type: string | ((props: Record<string, unknown>) => unknown);
  props: Record<string, unknown> & { children?: unknown };
  key: string | number | null;
}

export type VNode = VNodeElement;
export type VNodeChild =
  | VNodeElement
  | string
  | number
  | boolean
  | null
  | undefined
  | VNodeChild[];

const REACT_ELEMENT_SYMBOL = Symbol.for("react.element");

function createIsomorphicElement(
  type: string | ((props: Record<string, unknown>) => unknown),
  props: Record<string, unknown> | null,
  ...children: unknown[]
): VNodeElement {
  const flatChildren: unknown[] = [];
  const pushChild = (child: unknown): void => {
    if (Array.isArray(child)) {
      for (const nested of child) {
        pushChild(nested);
      }
    } else if (child !== null && child !== undefined && typeof child !== "boolean") {
      flatChildren.push(child);
    }
  };
  for (const child of children) {
    pushChild(child);
  }

  const normalizedProps: Record<string, unknown> & { children?: unknown } = {
    ...(props ?? {}),
  };
  if (flatChildren.length === 1) {
    normalizedProps.children = flatChildren[0];
  } else if (flatChildren.length > 1) {
    normalizedProps.children = flatChildren;
  }

  if (typeof type === "function") {
    return type(normalizedProps) as VNodeElement;
  }

  return {
    $$typeof: REACT_ELEMENT_SYMBOL,
    type,
    props: normalizedProps,
    key: normalizedProps.key !== undefined ? String(normalizedProps.key) : null,
  };
}

export const React = {
  createElement: createIsomorphicElement,
  Fragment: (props: { children?: unknown }) => props.children ?? null,
};

declare global {
  // eslint-disable-next-line @typescript-eslint/no-namespace
  namespace JSX {
    type Element = VNodeElement;
    interface IntrinsicElements {
      [elemName: string]: Record<string, unknown>;
    }
  }
}

// ---------------------------------------------------------------------------
// Vega-Lite v5 Validation & Extraction Utilities
// ---------------------------------------------------------------------------

const ALLOWED_MARK_TYPES = new Set<string>([
  "bar",
  "line",
  "rule",
  "point",
  "circle",
  "square",
  "tick",
  "area",
  "rect",
  "text",
  "trail",
  "geoshape",
  "arc",
  "boxplot",
  "errorband",
  "errorbar",
]);

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function extractMarkType(mark: unknown): string | null {
  if (typeof mark === "string" && mark.trim().length > 0) {
    return mark.trim();
  }
  if (isPlainObject(mark) && typeof mark.type === "string" && mark.type.trim().length > 0) {
    return mark.type.trim();
  }
  return null;
}

function hasValidEncodingChannel(encoding: unknown): boolean {
  if (!isPlainObject(encoding)) {
    return false;
  }
  const channels = ["x", "y", "x2", "y2", "theta", "radius", "text", "color", "latitude", "longitude"];
  return channels.some((channel) => isPlainObject(encoding[channel]));
}

function extractTitleText(title: unknown): string | null {
  if (typeof title === "string" && title.trim().length > 0) {
    return title.trim();
  }
  if (isPlainObject(title) && typeof title.text === "string" && title.text.trim().length > 0) {
    return title.text.trim();
  }
  return null;
}

function classifyUc1ChartKind(
  specObj: Record<string, unknown>,
  titleText: string | null,
  values: Array<Record<string, unknown>>
): SupportedUc1ChartKind | "generic_vega_lite_v5" {
  const explicitName = typeof specObj.name === "string" ? specObj.name.trim() : "";
  if (explicitName === "depot_stock_vs_demand_bar_chart") {
    return "depot_stock_vs_demand_bar_chart";
  }
  if (explicitName === "actuator_fatigue_threshold_chart") {
    return "actuator_fatigue_threshold_chart";
  }

  const combinedText = `${explicitName} ${titleText ?? ""} ${
    typeof specObj.description === "string" ? specObj.description : ""
  }`.toLowerCase();

  const sampleKeys = new Set<string>();
  for (const row of values.slice(0, 5)) {
    if (isPlainObject(row)) {
      for (const k of Object.keys(row)) {
        sampleKeys.add(k.toLowerCase());
      }
    }
  }

  if (
    combinedText.includes("depot") ||
    combinedText.includes("stock vs") ||
    combinedText.includes("demand") ||
    sampleKeys.has("quantity_on_hand") ||
    sampleKeys.has("quantity_reserved_30d") ||
    sampleKeys.has("depot_id") ||
    sampleKeys.has("depot_name")
  ) {
    return "depot_stock_vs_demand_bar_chart";
  }

  if (
    combinedText.includes("actuator") ||
    combinedText.includes("fatigue") ||
    combinedText.includes("threshold") ||
    combinedText.includes("condemnation") ||
    sampleKeys.has("current_flight_hours") ||
    sampleKeys.has("life_limit_threshold_hrs") ||
    sampleKeys.has("tail_number")
  ) {
    return "actuator_fatigue_threshold_chart";
  }

  return "generic_vega_lite_v5";
}

/**
 * Validates that a candidate JSON object strictly conforms to Vega-Lite v5
 * (`https://vega.github.io/schema/vega-lite/v5.json`) and contains a valid
 * inline dataset (`data.values`) and visual grammar (`mark` + `encoding` or `layer`).
 */
export function validateVegaLiteSpec(spec: unknown): VegaValidationResult {
  const errors: string[] = [];

  if (!isPlainObject(spec)) {
    return {
      valid: false,
      errors: ["Vega-Lite specification must be a non-null JSON object."],
      schemaVersion: null,
      chartKind: "invalid",
      rowCount: 0,
      titleText: null,
    };
  }

  const schemaVersion = typeof spec.$schema === "string" ? spec.$schema.trim() : null;
  if (schemaVersion !== VEGA_LITE_V5_SCHEMA) {
    errors.push(
      `Invalid or missing $schema: expected "${VEGA_LITE_V5_SCHEMA}", received "${String(spec.$schema ?? "undefined")}".`
    );
  }

  const titleText = extractTitleText(spec.title);

  // Validate inline data.values
  let values: Array<Record<string, unknown>> = [];
  if (!isPlainObject(spec.data)) {
    errors.push("Missing required `data` object in Vega-Lite v5 specification.");
  } else if (!Array.isArray(spec.data.values)) {
    errors.push("`data.values` must be an array of inline data objects.");
  } else if (spec.data.values.length === 0) {
    errors.push("`data.values` cannot be empty; at least one data record is required.");
  } else {
    const invalidRowIdx = spec.data.values.findIndex((item) => !isPlainObject(item));
    if (invalidRowIdx !== -1) {
      errors.push(`\`data.values[${invalidRowIdx}]\` must be a non-null object record.`);
    } else {
      values = spec.data.values as Array<Record<string, unknown>>;
    }
  }

  // Validate either single-view (`mark` + `encoding`) or layered view (`layer`)
  const hasLayers = Array.isArray(spec.layer);
  const hasSingleMark = spec.mark !== undefined;

  if (!hasLayers && !hasSingleMark) {
    errors.push("Specification must define either a top-level `mark` or a non-empty `layer` array.");
  }

  if (hasSingleMark) {
    const markType = extractMarkType(spec.mark);
    if (!markType || !ALLOWED_MARK_TYPES.has(markType)) {
      errors.push(
        `Invalid top-level \`mark\`: "${String(markType ?? spec.mark)}". Expected one of ${Array.from(ALLOWED_MARK_TYPES).join(", ")}.`
      );
    }
    if (!hasValidEncodingChannel(spec.encoding)) {
      errors.push("Single-view specification with `mark` must include a valid `encoding` object with at least one positional/visual channel.");
    }
  }

  if (hasLayers) {
    const layers = spec.layer as unknown[];
    if (layers.length === 0) {
      errors.push("`layer` array cannot be empty when specified.");
    } else {
      layers.forEach((layerItem, idx) => {
        if (!isPlainObject(layerItem)) {
          errors.push(`\`layer[${idx}]\` must be a valid layer object.`);
          return;
        }
        const layerMark = extractMarkType(layerItem.mark);
        if (!layerMark || !ALLOWED_MARK_TYPES.has(layerMark)) {
          errors.push(`\`layer[${idx}].mark\` is missing or unsupported ("${String(layerMark ?? layerItem.mark)}").`);
        }
        const combinedEncoding = isPlainObject(layerItem.encoding)
          ? { ...(isPlainObject(spec.encoding) ? spec.encoding : {}), ...layerItem.encoding }
          : spec.encoding;
        if (!hasValidEncodingChannel(combinedEncoding)) {
          errors.push(`\`layer[${idx}]\` is missing a valid \`encoding\` channel.`);
        }
      });
    }
  }

  const valid = errors.length === 0;
  return {
    valid,
    errors,
    schemaVersion,
    chartKind: valid ? classifyUc1ChartKind(spec, titleText, values) : "invalid",
    rowCount: values.length,
    titleText,
  };
}

/**
 * Extracts all code-fenced ```vega-lite (or ```json containing a vega-lite $schema)
 * JSON specifications from an agent Markdown response.
 */
export function extractVegaLiteBlocks(markdownOrAgentResponse: string): VegaLiteV5Spec[] {
  if (typeof markdownOrAgentResponse !== "string" || markdownOrAgentResponse.trim().length === 0) {
    return [];
  }

  const results: VegaLiteV5Spec[] = [];
  const fenceRegex = /```(?:vega-lite|json)\s*\r?\n([\s\S]*?)```/gi;
  let match: RegExpExecArray | null = fenceRegex.exec(markdownOrAgentResponse);

  while (match !== null) {
    const fullFenceHeader = match[0].slice(0, match[0].indexOf("\n")).toLowerCase();
    const rawBody = match[1].trim();
    if (rawBody.length > 0) {
      try {
        const parsed: unknown = JSON.parse(rawBody);
        if (isPlainObject(parsed)) {
          const isExplicitVegaFence = fullFenceHeader.includes("vega-lite");
          const hasVegaSchema =
            typeof parsed.$schema === "string" && parsed.$schema.includes("vega-lite");
          if (isExplicitVegaFence || hasVegaSchema) {
            results.push(parsed as unknown as VegaLiteV5Spec);
          }
        }
      } catch {
        // Ignore non-JSON or malformed blocks while continuing extraction
      }
    }
    match = fenceRegex.exec(markdownOrAgentResponse);
  }

  return results;
}

// ---------------------------------------------------------------------------
// Dual-Compatible Markdown Fallback Table Formatting (Zero Math Invention)
// ---------------------------------------------------------------------------

interface NormalizedTableRow {
  tailNumber: string;
  partSerialNumber: string;
  currentHours: string;
  limitHours: string;
  variance: string;
  depotStock: string;
  readinessStatus: string;
  assignedSortie: string;
}

function formatVerbatimCell(val: unknown, fallback = "—"): string {
  if (val === null || val === undefined || val === "") {
    return fallback;
  }
  return String(val);
}

function normalizeSummaryRow(row: ActuatorSummaryTableRow): NormalizedTableRow {
  const tailNumber = formatVerbatimCell(row.tailNumber ?? row.tail_number);
  const partSerialNumber = formatVerbatimCell(
    row.partSerialNumber ?? row.part_serial_number ?? row.part_sn
  );
  const currentHours = formatVerbatimCell(row.currentHours ?? row.current_flight_hours);
  const limitHours = formatVerbatimCell(row.limitHours ?? row.life_limit_threshold_hrs);
  const variance = formatVerbatimCell(
    row.variance ?? row.variance_hrs ?? row.hours_variance
  );
  const depotStock = formatVerbatimCell(
    row.depotStock ?? row.depot_stock_on_hand ?? row.quantity_on_hand
  );
  const readinessStatus = formatVerbatimCell(
    row.readinessStatus ?? row.readiness_status ?? row.aircraft_status
  );
  const assignedSortie = formatVerbatimCell(
    row.assignedSortie ?? row.assigned_sortie ?? row.sortie_id
  );

  return {
    tailNumber,
    partSerialNumber,
    currentHours,
    limitHours,
    variance,
    depotStock,
    readinessStatus,
    assignedSortie,
  };
}

/**
 * Renders the dual-compatible Markdown fallback table required for environments
 * without canvas execution (`agents-cli playground`, `agents-cli eval`).
 * Strictly formats values passed in `rows` without inventing or recalculating figures.
 */
export function renderMarkdownFallbackTable(rows: ActuatorSummaryTableRow[]): string {
  const header =
    "| Tail Number | Part S/N | Current Hours | Limit Hours | Variance | Depot Stock | Readiness Status | Assigned Sortie |";
  const divider =
    "| :--- | :--- | ---: | ---: | ---: | ---: | :--- | :--- |";

  if (!Array.isArray(rows) || rows.length === 0) {
    return `${header}\n${divider}\n| — | — | — | — | — | — | — | — |`;
  }

  const bodyLines = rows.map((rawRow) => {
    const r = normalizeSummaryRow(rawRow);
    return `| ${r.tailNumber} | ${r.partSerialNumber} | ${r.currentHours} | ${r.limitHours} | ${r.variance} | ${r.depotStock} | ${r.readinessStatus} | ${r.assignedSortie} |`;
  });

  return [header, divider, ...bodyLines].join("\n");
}

/**
 * Formats a complete dual-compatible visual artifact containing both code-fenced
 * ```vega-lite v5 JSON specification block(s) and the Markdown fallback data table,
 * satisfying `/packages/web/AGENTS.md` Invariant #2.
 */
export function formatDualCompatibleVegaOutput(
  specs: VegaLiteV5Spec | VegaLiteV5Spec[] | Record<string, VegaLiteV5Spec>,
  rows: ActuatorSummaryTableRow[]
): string {
  const specList: VegaLiteV5Spec[] = Array.isArray(specs)
    ? specs
    : isPlainObject(specs) && "$schema" in specs
      ? [specs as VegaLiteV5Spec]
      : isPlainObject(specs)
        ? (Object.values(specs) as VegaLiteV5Spec[])
        : [];

  const fencedBlocks = specList.map((specItem) => {
    const validation = validateVegaLiteSpec(specItem);
    if (!validation.valid) {
      throw new Error(
        `Cannot emit invalid Vega-Lite v5 specification: ${validation.errors.join(" ")}`
      );
    }
    return `\`\`\`vega-lite\n${JSON.stringify(specItem, null, 2)}\n\`\`\``;
  });

  const markdownTable = renderMarkdownFallbackTable(rows);
  return [...fencedBlocks, "", markdownTable].join("\n");
}

// ---------------------------------------------------------------------------
// Responsive Table Styles (modern-web-guidance: `responsive-table`)
// ---------------------------------------------------------------------------

export const VEGA_CANVAS_RESPONSIVE_TABLE_CSS = `
.table-wrapper {
  overflow: auto;
  max-inline-size: 100%;
  max-block-size: min(500px, 80vh);
  container-type: inline-size;
  border: 1px solid #cbd5e1;
  border-radius: 0.5rem;
}

.table-wrapper table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-family: system-ui, -apple-system, sans-serif;
  font-size: 0.875rem;
  --label-1: "Tail Number";
  --label-2: "Part S/N";
  --label-3: "Current Hours";
  --label-4: "Limit Hours";
  --label-5: "Variance";
  --label-6: "Depot Stock";
  --label-7: "Readiness Status";
  --label-8: "Assigned Sortie";
}

.table-wrapper thead {
  position: sticky;
  inset-block-start: 0;
  z-index: 1;
  background: #0f172a;
  color: #f8fafc;
}

.table-wrapper tbody th {
  position: sticky;
  inset-inline-start: 0;
  background: #ffffff;
  font-weight: 600;
}

@container (width < 600px) {
  .table-wrapper table,
  .table-wrapper thead,
  .table-wrapper tbody,
  .table-wrapper tr,
  .table-wrapper th,
  .table-wrapper td {
    display: block;
  }

  .table-wrapper thead {
    display: none;
  }

  .table-wrapper tr {
    margin-block-end: 1.5rem;
    border: 1px solid #cbd5e1;
  }

  .table-wrapper tbody th {
    position: sticky;
    inset-block-start: 0;
    z-index: 2;
    background: #f1f5f9;
  }

  .table-wrapper td:nth-child(2)::before { content: var(--label-2) ": "; font-weight: 600; }
  .table-wrapper td:nth-child(3)::before { content: var(--label-3) ": "; font-weight: 600; }
  .table-wrapper td:nth-child(4)::before { content: var(--label-4) ": "; font-weight: 600; }
  .table-wrapper td:nth-child(5)::before { content: var(--label-5) ": "; font-weight: 600; }
  .table-wrapper td:nth-child(6)::before { content: var(--label-6) ": "; font-weight: 600; }
  .table-wrapper td:nth-child(7)::before { content: var(--label-7) ": "; font-weight: 600; }
  .table-wrapper td:nth-child(8)::before { content: var(--label-8) ": "; font-weight: 600; }
}
`.trim();

export const VEGA_CANVAS_RESPONSIVE_TABLE_STYLES = VEGA_CANVAS_RESPONSIVE_TABLE_CSS;

// ---------------------------------------------------------------------------
// VegaCanvas React Component
// ---------------------------------------------------------------------------

function collectSpecsFromProps(props: VegaCanvasProps): VegaLiteV5Spec[] {
  const collected: VegaLiteV5Spec[] = [];

  if (props.depotStockVsDemandChart) {
    collected.push(props.depotStockVsDemandChart);
  }
  if (props.actuatorFatigueThresholdChart) {
    collected.push(props.actuatorFatigueThresholdChart);
  }
  if (props.spec) {
    collected.push(props.spec);
  }
  if (Array.isArray(props.specs)) {
    collected.push(...props.specs);
  } else if (isPlainObject(props.specs)) {
    for (const val of Object.values(props.specs)) {
      if (isPlainObject(val)) {
        collected.push(val as VegaLiteV5Spec);
      }
    }
  }
  if (props.agentResponseMarkdown) {
    const extracted = extractVegaLiteBlocks(props.agentResponseMarkdown);
    collected.push(...extracted);
  }

  return collected;
}

/**
 * Renders interactive Vega-Lite v5 visual specifications alongside a responsive semantic
 * HTML table and dual-compatible Markdown fallback table for UC1 (`@F35-Sustainment-Analytics`).
 */
export function VegaCanvas(props: VegaCanvasProps): JSX.Element {
  const {
    summaryRows,
    supplyRecommendation,
    tableCaptionId = "uc1-actuator-telemetry-caption",
    tableCaption = "F-35 Fleet Horizontal Tail Actuator Telemetry, Regional Depot Stock & Sortie Schedule",
    showVegaLiteSource = true,
  } = props;

  const specs = collectSpecsFromProps(props);
  const validations = specs.map((specItem) => ({
    spec: specItem,
    validation: validateVegaLiteSpec(specItem),
  }));

  const normalizedRows = (summaryRows ?? []).map(normalizeSummaryRow);
  const markdownFallback = renderMarkdownFallbackTable(summaryRows ?? []);

  return (
    <section
      className="f35-vega-canvas-studio"
      aria-label="F-35 Sustainment Analytics & Vega-Lite Visual Canvas"
      data-component="VegaCanvas"
      data-schema={VEGA_LITE_V5_SCHEMA}
    >
      <style>{VEGA_CANVAS_RESPONSIVE_TABLE_CSS}</style>

      <div className="f35-vega-charts-grid" role="group" aria-label="Vega-Lite v5 Visual Specifications">
        {validations.map(({ spec: chartSpec, validation }, idx) => {
          if (!validation.valid) {
            return (
              <div
                key={`invalid-spec-${idx}`}
                role="alert"
                className="f35-vega-validation-error"
                data-valid="false"
              >
                <strong>Vega-Lite v5 Schema Validation Error:</strong>
                <ul>
                  {validation.errors.map((err, errIdx) => (
                    <li key={`err-${errIdx}`}>{err}</li>
                  ))}
                </ul>
              </div>
            );
          }

          const chartTitle =
            validation.titleText ??
            (validation.chartKind === "depot_stock_vs_demand_bar_chart"
              ? "Regional Depot Stock vs. 30-Day Demand (NSN 1680-01-619-4821)"
              : validation.chartKind === "actuator_fatigue_threshold_chart"
                ? "Horizontal Tail Actuator Flight Hours vs. 1,000.0-Hr Condemnation Limit"
                : `Vega-Lite v5 Chart #${idx + 1}`);

          return (
            <figure
              key={`vega-chart-${validation.chartKind}-${idx}`}
              className="f35-vega-chart-card"
              data-valid="true"
              data-chart-kind={validation.chartKind}
              data-row-count={String(validation.rowCount)}
            >
              <figcaption className="f35-vega-chart-title">
                <h4>{chartTitle}</h4>
                <span className="f35-vega-schema-badge">{validation.schemaVersion}</span>
              </figcaption>

              <div
                className="f35-vega-datapoint-list"
                role="list"
                aria-label={`${chartTitle} Data Points`}
              >
                {chartSpec.data.values.map((datum, rowIdx) => (
                  <div
                    key={`datum-${rowIdx}`}
                    role="listitem"
                    className="f35-vega-datum-pill"
                    data-row-index={String(rowIdx)}
                  >
                    {Object.entries(datum).map(([k, v]) => (
                      <span key={k} className="f35-vega-datum-kv" data-field={k}>
                        <strong>{k}:</strong> {String(v)}
                      </span>
                    ))}
                  </div>
                ))}
              </div>

              {showVegaLiteSource ? (
                <pre className="f35-vega-fenced-block" aria-label="Fenced Vega-Lite v5 Specification">
                  <code className="language-vega-lite">
                    {JSON.stringify(chartSpec, null, 2)}
                  </code>
                </pre>
              ) : null}
            </figure>
          );
        })}
      </div>

      {supplyRecommendation ? (
        <aside
          className="f35-supply-recommendation-banner"
          aria-label="Automated Supply Alert & Sortie Tail-Swap Recommendation"
          data-nsn={supplyRecommendation.nsn}
        >
          <h4>Supply Replenishment &amp; Sortie Reallocation</h4>
          <p>
            <strong>NSN:</strong> {supplyRecommendation.nsn} |{" "}
            <strong>On-Hand Stock:</strong> {String(supplyRecommendation.quantityOnHand)} |{" "}
            <strong>30-Day Reserved Demand:</strong> {String(supplyRecommendation.quantityReserved30d)} |{" "}
            <strong>Shipping ETA:</strong> {String(supplyRecommendation.avgShippingEtaHours)} hrs
          </p>
          {supplyRecommendation.sortieId ? (
            <p data-sortie-id={supplyRecommendation.sortieId}>
              <strong>Sortie Reallocation:</strong> {supplyRecommendation.sortieId} (
              {supplyRecommendation.assignedPilotCallsign ?? "Assigned Pilot"}) swapped from{" "}
              <span className="tail-breach">{supplyRecommendation.primaryTail}</span> to serviceable spare{" "}
              <span className="tail-serviceable">{supplyRecommendation.spareTail}</span>.
            </p>
          ) : null}
        </aside>
      ) : null}

      <div
        tabIndex={0}
        role="region"
        aria-labelledby={tableCaptionId}
        className="table-wrapper"
      >
        <table>
          <caption id={tableCaptionId}>{tableCaption}</caption>
          <thead>
            <tr>
              <th scope="col">Tail Number</th>
              <th scope="col">Part S/N</th>
              <th scope="col">Current Hours</th>
              <th scope="col">Limit Hours</th>
              <th scope="col">Variance</th>
              <th scope="col">Depot Stock</th>
              <th scope="col">Readiness Status</th>
              <th scope="col">Assigned Sortie</th>
            </tr>
          </thead>
          <tbody>
            {normalizedRows.map((row, rIdx) => (
              <tr key={`row-${row.tailNumber}-${rIdx}`} data-tail={row.tailNumber}>
                <th scope="row">{row.tailNumber}</th>
                <td>{row.partSerialNumber}</td>
                <td>{row.currentHours}</td>
                <td>{row.limitHours}</td>
                <td>{row.variance}</td>
                <td>{row.depotStock}</td>
                <td>{row.readinessStatus}</td>
                <td>{row.assignedSortie}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <details className="f35-markdown-fallback-details" open>
        <summary>Dual-Compatible Markdown Data Table</summary>
        <pre className="f35-markdown-table-block" data-testid="markdown-fallback-table">
          <code>{markdownFallback}</code>
        </pre>
      </details>
    </section>
  );
}

export default VegaCanvas;
