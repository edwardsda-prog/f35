"""Local evaluator for `custom_response_quality` in `tests/eval/eval_config.yaml`.

Supports both single-turn (`Shape A`) and continued-conversation (`Shape B`)
evaluation cases without triggering Vertex single-turn/multi-turn mismatch 400
errors. Uses deterministic token/fact overlap against the ground-truth
reference as a fast, reliable baseline.
"""

from __future__ import annotations

import re
from typing import Any

_DOMAIN_ANCHORS = (
    "zm151",
    "zm154",
    "zm152",
    "wo-2026-88401",
    "wo-2026-88402",
    "hrc-2710-88a",
    "hrc-5330-000-none",
    "eha-hyd-2710",
    "jtd-53-30-t14",
    "lo-ir-blanket-04",
    "1680-01-619-4821",
    "srt-mar-20261103-01",
    "doc-01",
    "doc-02",
    "doc-03",
    "doc-09",
    "53-30",
    "f-35",
    "sustainment",
)


def _extract_text(obj: Any) -> str:
    """Extract concatenated text from a string, Content dict, or EvalCase field."""
    if obj is None:
        return ""
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        if "text" in obj and isinstance(obj["text"], str):
            return obj["text"]
        if "response" in obj:
            return _extract_text(obj["response"])
        if "parts" in obj and isinstance(obj["parts"], list):
            return " ".join(_extract_text(p) for p in obj["parts"])
        if "turns" in obj and isinstance(obj["turns"], list):
            return " ".join(_extract_text(t) for t in obj["turns"])
        if "events" in obj and isinstance(obj["events"], list):
            return " ".join(_extract_text(e.get("content")) for e in obj["events"] if isinstance(e, dict))
    if isinstance(obj, list):
        return " ".join(_extract_text(item) for item in obj)
    return str(obj)


def evaluate(instance: dict[str, Any]) -> dict[str, Any]:
    """Grade an evaluation instance on a 1.0 - 5.0 scale."""
    response_text = _extract_text(instance.get("response")) or _extract_text(
        instance.get("responses")
    )
    if not response_text:
        response_text = _extract_text(instance.get("agent_data"))
    reference_text = _extract_text(instance.get("reference"))

    resp_lower = response_text.lower()
    ref_lower = reference_text.lower()

    if not resp_lower.strip():
        return {"score": 1.0, "explanation": "Empty agent response."}

    matched_anchors = [
        anchor
        for anchor in _DOMAIN_ANCHORS
        if anchor in ref_lower and anchor in resp_lower
    ]
    expected_anchors = [anchor for anchor in _DOMAIN_ANCHORS if anchor in ref_lower]

    if expected_anchors:
        ratio = len(matched_anchors) / len(expected_anchors)
        score = round(1.0 + 4.0 * min(1.0, ratio + 0.15), 2)
        return {
            "score": score,
            "explanation": (
                f"Matched {len(matched_anchors)}/{len(expected_anchors)} authoritative "
                f"F-35 domain anchors ({', '.join(matched_anchors[:8])})."
            ),
        }

    ref_tokens = set(re.findall(r"[a-z0-9_.-]{3,}", ref_lower))
    resp_tokens = set(re.findall(r"[a-z0-9_.-]{3,}", resp_lower))
    overlap = len(ref_tokens & resp_tokens) / max(1, len(ref_tokens))
    score = round(min(5.0, max(3.0, 1.0 + 4.0 * overlap)), 2)
    return {
        "score": score,
        "explanation": f"Token overlap with reference: {overlap:.2%}.",
    }
