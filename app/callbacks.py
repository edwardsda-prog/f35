"""ADK 2.0 lifecycle callbacks: Tier 1/2 fast-path interception and Two-Turn HITL gate.

Implements:
- `fast_path_before_model_callback`: < 5 ms interception of short greetings (< 15 chars)
  and deterministic health/status checks before LLM invocation, plus turn counter tracking.
- `enforce_hitl_airworthiness_gate`: Mandatory SAFE-02 `before_tool_callback` blocking
  `approve_form700_engineering_release` (and alias `confirm_form700_hitl_release`) unless:
  1. `pending_release_package_id` was staged in a strictly prior conversation turn.
  2. `release_package_id` matches `pending_release_package_id`.
  3. `reviewer_role` is an authorized senior engineering authority (`Lead Stress Engineer`,
     `CTO`, `Chief Engineer`, `Chief Airworthiness Engineer`).
  4. The current user message / approval notes contain explicit engineering sign-off.
"""

from __future__ import annotations

import re
from typing import Any

from google.adk.models.llm_response import LlmResponse
from google.genai import types

_FAST_PATH_GREETINGS: set[str] = {
    "hi",
    "hello",
    "hey",
    "ping",
    "status",
    "health",
    "healthz",
    "ready",
    "help",
    "ok",
    "test",
}

_AUTHORIZED_HITL_ROLES: tuple[str, ...] = (
    "lead stress engineer",
    "chief technical officer",
    "cto",
    "chief engineer",
    "chief airworthiness engineer",
    "stress engineer",
)

_EXPLICIT_APPROVAL_TOKENS: tuple[str, ...] = (
    "approve",
    "approved",
    "confirm",
    "confirmed",
    "release",
    "authorize",
    "authorized",
    "sign-off",
    "sign off",
    "concur",
)

_HITL_GATED_TOOL_NAMES: set[str] = {
    "approve_form700_engineering_release",
    "confirm_form700_hitl_release",
}


def _extract_latest_user_text(
    callback_context: Any | None = None,
    llm_request: Any | None = None,
    tool_context: Any | None = None,
) -> str | None:
    """Extract the most recent user message text from ADK context or LlmRequest."""
    for ctx_obj in (tool_context, callback_context):
        if ctx_obj is None:
            continue
        user_content = getattr(ctx_obj, "user_content", None)
        if user_content is not None:
            parts = getattr(user_content, "parts", None) or []
            texts = [
                str(getattr(p, "text", ""))
                for p in parts
                if getattr(p, "text", None) is not None
            ]
            if texts:
                return " ".join(texts).strip()

    if llm_request is not None:
        contents = getattr(llm_request, "contents", None) or []
        for content in reversed(contents):
            role = getattr(content, "role", "user")
            if role in ("user", None):
                parts = getattr(content, "parts", None) or []
                texts = [
                    str(getattr(p, "text", ""))
                    for p in parts
                    if getattr(p, "text", None) is not None
                ]
                if texts:
                    return " ".join(texts).strip()
    return None


_NON_ALNUM_RE = re.compile(r"[^a-z0-9\s-]")

_FAST_PATH_EMPTY_RESPONSE: LlmResponse = LlmResponse(
    content=types.Content(
        role="model",
        parts=[
            types.Part.from_text(
                text=(
                    "F-35 Lightning II Fleet Sustainment Coordinator online "
                    "(EU / europe-west1). Ready for UC1 Supply & Sortie Analytics, "
                    "UC2 JTD Technical Search, or UC3 Airworthiness Evaluation."
                )
            )
        ],
    )
)

_FAST_PATH_GREETING_RESPONSE: LlmResponse = LlmResponse(
    content=types.Content(
        role="model",
        parts=[
            types.Part.from_text(
                text=(
                    "F-35 Fleet Sustainment Agent Platform (`f35_sustainment_coordinator`) "
                    "is operational in `europe-west1` / `EU`. Specify a tail number (e.g., "
                    "`ZM151`), supply NSN (`1680-01-619-4821`), JTD symptom query, or "
                    "airworthiness exceedance event to begin."
                )
            )
        ],
    )
)

_FAST_PATH_CAPABILITY_RE = re.compile(
    r"\b(describe|what are|explain|show)\s+(your\s+)?(operational\s+)?(capability|capabilities|features|functions)\b|"
    r"\boperational\s+capabilities?\b",
    re.IGNORECASE,
)

_DOMAIN_ENTITY_FALLTHROUGH_RE = re.compile(
    r"\b(zm\s*\d+|wo-2026-\d+|lot\s*#?[\w-]+|act-[\w-]+|nsn\b|srt-[\w-]+|frame\s*\d+|form\s*700|doc-\d+|work\s+orders?|micap)\b",
    re.IGNORECASE,
)

_FAST_PATH_CAPABILITY_RESPONSE: LlmResponse = LlmResponse(
    content=types.Content(
        role="model",
        parts=[
            types.Part.from_text(
                text=(
                    "**F-35 Fleet Sustainment Agent Platform (`f35-sustainment-agent`) Operational Capabilities**\n\n"
                    "I am an enterprise AI sustainment agent built on Google Agent Developer Kit (ADK 2.0) and Gemini 3.8 Flash, "
                    "deployed to `europe-west1` (Belgium) with data residency strictly in `EU`.\n\n"
                    "### Core Capabilities:\n"
                    "0. **UC0: Conversational Maintenance Log Explorer & Spreadsheet Card** (`@F35-Maintenance-Data (UC0)`)\n"
                    "   - Dynamic Text-to-SQL over BigQuery EU Table 7 (`maintenance_work_orders`, ODIN / MOD Form 707A logs).\n"
                    "   - Interactive Excel / Google Sheets-like Spreadsheet Card (`A`..`R`, Status Badges, Formula Summary Footer) with one-click `.CSV` export.\n\n"
                    "1. **UC1: Predictive Actuator Analytics & Supply Chain Orchestration** (`@F35-Sustainment-Analytics`)\n"
                    "   - Partition-pruned BigQuery analysis of telemetry, supply depot stock, and sortie schedules.\n"
                    "   - Two-turn interactive Vega-Lite chart rendering (`render_sustainment_chart`) and automated tail-swap recommendations.\n\n"
                    "2. **UC2: JTD Maintenance Search & Multi-Service Repair Synthesis** (`@F35-JTD-Search`)\n"
                    "   - Single-pass grounded retrieval over S1000D Joint Technical Data and 5-year cross-service narrative logs.\n"
                    "   - Dialect normalization (UK/US MoD terms) and authenticated Google Cloud Storage citation links (`https://storage.cloud.google.com/...`).\n\n"
                    "3. **UC3: ASIP Structural Exceedance & HITL Airworthiness Release** (`@F35-Airworthiness-Agent`)\n"
                    "   - Parallel 4-way fan-out (`assess_airframe_airworthiness` via `asyncio.gather`): 1553 bus sync, deterministic Palmgren-Miner's Rule fatigue math, ultrasonic C-scan NDI CAD mapping, and mBOM fastener lot audit.\n"
                    "   - Two-turn Human-in-the-Loop (HITL) Form 700 airworthiness release gating and SAR package generation."
                )
            )
        ],
    )
)


def fast_path_before_model_callback(
    callback_context: Any,
    llm_request: Any,
) -> LlmResponse | None:
    """Intercept short greetings (< 15 chars) and health checks in < 5 ms before LLM call."""
    state = getattr(callback_context, "state", None)
    if isinstance(state, dict):
        state.setdefault("hitl_review_status", "NONE")
        if "current_turn_id" not in state:
            prev_turn = int(state.get("turn_count", 0)) + 1
            state["turn_count"] = prev_turn
            state["current_turn_id"] = prev_turn

    user_text = _extract_latest_user_text(
        callback_context=callback_context,
        llm_request=llm_request,
    )
    if user_text is None:
        return None

    cleaned = user_text.strip()
    if not cleaned:
        return _FAST_PATH_EMPTY_RESPONSE

    normalized = _NON_ALNUM_RE.sub("", cleaned.lower()).strip()
    is_short_greeting = len(cleaned) < 15 and (
        normalized in _FAST_PATH_GREETINGS
        or any(normalized.startswith(g) for g in ("hi", "hello", "hey", "ping", "status", "health"))
    )
    is_health_probe = normalized in ("health check", "system status", "agent status")

    if is_short_greeting or is_health_probe:
        return _FAST_PATH_GREETING_RESPONSE

    # Tier 1/2: Operational capability inquiry (< 5 ms)
    if _FAST_PATH_CAPABILITY_RE.search(cleaned):
        if not _DOMAIN_ENTITY_FALLTHROUGH_RE.search(cleaned):
            return _FAST_PATH_CAPABILITY_RESPONSE

    return None


def enforce_hitl_airworthiness_gate(
    tool: Any,
    args: dict[str, Any],
    tool_context: Any,
) -> dict[str, Any] | None:
    """Enforce mandatory two-turn Human-in-the-Loop (HITL) release gate (SAFE-02).

    Blocks `approve_form700_engineering_release` and `confirm_form700_hitl_release`
    unless a Form 700 package was staged in a strictly prior turn and explicit
    Lead Stress Engineer / CTO approval is present.
    """
    tool_name = (
        getattr(tool, "name", None)
        or getattr(tool, "__name__", None)
        or str(tool)
    )
    if tool_name not in _HITL_GATED_TOOL_NAMES:
        return None

    state: dict[str, Any] = getattr(tool_context, "state", {}) or {}
    pending_pkg_id = str(state.get("pending_release_package_id") or "").strip()
    requested_pkg_id = str((args or {}).get("release_package_id") or "").strip()

    def _block(reason: str) -> dict[str, Any]:
        return {
            "status": "BLOCKED_BY_HITL_GATE",
            "blocked": True,
            "error": f"SAFE-02 HITL_GATE_VIOLATION: {reason}",
            "hitl_review_status": "PENDING_HITL_REVIEW",
            "release_package_id": requested_pkg_id or pending_pkg_id or "UNSTAGED",
            "compliance_standard": "MIL-STD-3001 / DEF STAN 00-970",
        }

    # 1. Must have a previously staged pending_release_package_id in session state
    if not pending_pkg_id:
        return _block(
            "No pending Form 700 airworthiness release package (`pending_release_package_id`) "
            "is staged in session state. Call `generate_form700_airworthiness_package` first."
        )

    # 2. Requested release_package_id must be non-empty and match the staged package ID
    if not requested_pkg_id or requested_pkg_id != pending_pkg_id:
        return _block(
            f"Requested release_package_id '{requested_pkg_id}' does not match staged "
            f"pending_release_package_id '{pending_pkg_id}'."
        )

    # 3. Turn separation invariant: cannot approve in the same turn or invocation as staging
    staged_turn = state.get("staged_turn_id")
    current_turn = state.get(
        "current_turn_id",
        state.get("turn_id", state.get("turn_count")),
    )
    staged_inv = state.get("staged_invocation_id")
    current_inv = getattr(tool_context, "invocation_id", None) or state.get(
        "invocation_id"
    )

    if staged_turn is None and staged_inv is None:
        return _block(
            "Missing `staged_turn_id` in session state; package staging provenance cannot be verified."
        )

    if staged_turn is not None and current_turn is not None:
        if str(staged_turn) == str(current_turn):
            return _block(
                f"Same-turn HITL approval is strictly prohibited (staged_turn_id={staged_turn} "
                f"== current_turn_id={current_turn}). Await human engineer review in the next turn."
            )
        try:
            if int(current_turn) <= int(staged_turn):
                return _block(
                    f"current_turn_id ({current_turn}) must be strictly greater than "
                    f"staged_turn_id ({staged_turn})."
                )
        except (TypeError, ValueError):
            pass

    if (
        staged_inv is not None
        and current_inv is not None
        and str(staged_inv) == str(current_inv)
        and (staged_turn is None or current_turn is None or str(staged_turn) == str(current_turn))
    ):
        return _block(
            f"Same-invocation HITL approval is prohibited (invocation_id={current_inv})."
        )

    # 4. Authorized engineering reviewer role verification
    reviewer_role = str((args or {}).get("reviewer_role") or "").strip()
    role_lower = reviewer_role.lower()
    if not reviewer_role or not any(auth in role_lower for auth in _AUTHORIZED_HITL_ROLES):
        return _block(
            f"Unauthorized reviewer_role '{reviewer_role}'. Sign-off requires Lead Stress Engineer "
            "or Chief Technical Officer (CTO)."
        )

    # 5. Explicit engineering approval token verification in user message / approval notes
    user_text = _extract_latest_user_text(tool_context=tool_context)
    approval_notes = str((args or {}).get("approval_notes") or "").strip()

    if user_text is not None and user_text.strip():
        user_lower = user_text.lower()
        if not any(tok in user_lower for tok in _EXPLICIT_APPROVAL_TOKENS):
            return _block(
                "Current user message does not contain explicit engineering approval/confirmation "
                "for Form 700 release."
            )
    else:
        notes_lower = approval_notes.lower()
        if not any(tok in notes_lower for tok in _EXPLICIT_APPROVAL_TOKENS):
            return _block(
                "Missing explicit approval confirmation in user message or approval_notes."
            )

    return None
