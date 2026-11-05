"""ADK 2.0 lifecycle callbacks: Tier 1/2 fast-path interception (< 5 ms).

Implements:
- `fast_path_before_model_callback`: < 5 ms interception of short greetings (< 15 chars),
  deterministic health/status checks, and operational capability inquiries before LLM invocation.
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
                    "F-35 Lightning II Fleet Sustainment Coordinator online. "
                    "Ready to assist with maintenance work orders, PHM/BIT fault triage, "
                    "SQEP tooling dispatch, component supply analytics, or technical publications."
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
                    "F-35 Fleet Sustainment Agent Platform is operational. "
                    "Specify a tail number (e.g., `ZM151`), supply NSN (`1680-01-619-4821`), "
                    "work order / PHM fault query, or technical manual symptom to begin."
                )
            )
        ],
    )
)

_FAST_PATH_CAPABILITY_RE = re.compile(
    r"\b(describe|what\s+are|explain|show)\s+(your\s+)?(operational\s+)?(capability|capabilities|features|functions)\b|"
    r"\boperational\s+capabilit(?:y|ies)\b",
    re.IGNORECASE,
)

_DOMAIN_ENTITY_FALLTHROUGH_RE = re.compile(
    r"\b(zm\s*\d+|wo-2026-\d+|phm-2026-\d+|res-2026-\d+|hrc-[\w-]+|lot\s*#?[\w-]+|act-[\w-]+|nsn\b|srt-[\w-]+|frame\s*\d+|form\s*700|doc-\d+|work\s+orders?|micap|sqep\b|qar\b|cnd\b|phm_bit_fault_events|work_center_tooling_and_sqep)\b",
    re.IGNORECASE,
)

_FAST_PATH_CAPABILITY_RESPONSE: LlmResponse = LlmResponse(
    content=types.Content(
        role="model",
        parts=[
            types.Part.from_text(
                text=(
                    "**F-35 Fleet Sustainment Agent Platform**\n\n"
                    "An intelligent sustainment and engineering decision-support platform for the F-35 Lightning II fleet.\n\n"
                    "**Core Purpose & Operational Benefits:**\n"
                    "- **Accelerate Fleet Readiness:** Rapidly analyses maintenance work orders, ODIN PHM/BIT fault logs, SQEP shift tooling readiness, and global depot inventory across operational squadrons and carrier strike groups to eliminate mission-impairing bottlenecks.\n"
                    "- **Actionable Decision Support:** Recommends timely maintenance interventions, parts replenishment, sortie aircraft swaps, and executive 16:9 briefing graphics to maximize sortie generation rates.\n"
                    "- **Authoritative Engineering Guidance:** Synthesizes verified S1000D Joint Technical Data (JTD) manuals and 5-year cross-service historical repair narratives with bidirectional UK/US terminology normalization and verbatim citations.\n\n"
                    "How can I assist your squadron or maintenance control team today?"
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


__all__ = ["fast_path_before_model_callback"]
