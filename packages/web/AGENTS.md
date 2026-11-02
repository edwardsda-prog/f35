# Frontend Implementer Boundary — `/packages/web`

> **Scope:** Frontend Implementer Subagent  
> **Mandatory Guidelines:** Review root `AGENTS.md` and `.agents-cli-spec.md` for platform invariants.

## Responsibilities
- Dual-compatible Vega-Lite v5 JSON visual specifications emitted by UC1 tools for Gemini Enterprise Canvas rendering.
- Markdown table structures mirroring Vega-Lite chart payloads for environments lacking canvas execution (`agents-cli playground`, `agents-cli eval`).
- Form 700 / AFTO Form 781 airworthiness review component templates and HITL review confirmation dialog structures.

## Invariants
- Visual specifications must strictly conform to Vega-Lite schema `https://vega.github.io/schema/vega-lite/v5.json`.
- Dual output requirement: every visual artifact must provide both a code-fenced ```` ```vega-lite ```` specification and a formatted Markdown data table.
