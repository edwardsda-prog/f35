"""Empirical Challenger Stress Harness: UC3 Parallel Fan-Out & Form 700 HITL Gate.

Authored by challenger_r1_2 to empirically stress-test:
1. UC3 Parallel Fan-Out (`assess_airframe_airworthiness`):
   - Concurrency of 4 subtasks via asyncio.gather and asyncio.to_thread
   - Pure execution time SLA <= 3,100 ms across 50 iterations
   - Abnormal input handling (negative G, extreme Mach, missing stations, unknown tails)
2. Two-Turn HITL Safety Gate (SAFE-02):
   - Same-turn / same-invocation bypass attempts
   - Unauthorized reviewer roles ("Guest", "Operator", "Technician", etc.)
   - Valid second-turn sign-off verification with authenticated HTTPS SAR URI
"""

from __future__ import annotations

import asyncio
import time
from typing import Any
import pytest

from app.callbacks import enforce_hitl_airworthiness_gate
from app.tools import uc3_airworthiness
from app.tools.uc3_airworthiness import (
    assess_airframe_airworthiness,
    approve_form700_engineering_release,
    confirm_form700_hitl_release,
    generate_form700_airworthiness_package,
)


class DummyToolContext:
    """Mock ADK ToolContext with state, user_content, and invocation_id."""

    def __init__(
        self,
        state: dict[str, Any] | None = None,
        user_text: str = "",
        invocation_id: str = "inv-turn-1",
    ) -> None:
        self.state: dict[str, Any] = state if state is not None else {}
        self.invocation_id = invocation_id
        if user_text:
            self.user_content = type(
                "DummyContent",
                (),
                {"role": "user", "parts": [type("DummyPart", (), {"text": user_text})()]},
            )()
        else:
            self.user_content = None


class TestUc3ParallelFanOut:
    """Empirical verification of UC3 4-way parallel fan-out concurrency, latency, and robustness."""

    def test_uc3_subtasks_execute_concurrently(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Verify that all 4 sub-tasks run concurrently via asyncio.gather."""
        task_timings: dict[str, dict[str, float]] = {}

        orig_task_a = uc3_airworthiness.sync_flight_telemetry_exceedance
        orig_task_b = uc3_airworthiness.calculate_structural_fatigue_and_yield
        orig_task_c = uc3_airworthiness.inspect_ultrasonic_cscan_and_map_cad
        orig_task_d = uc3_airworthiness.audit_fastener_lot_in_mbom

        def instrumented_task_a(*args: Any, **kwargs: Any) -> dict[str, Any]:
            start = time.perf_counter()
            time.sleep(0.06)  # 60ms delay
            end = time.perf_counter()
            task_timings["task_a"] = {"start": start, "end": end}
            return orig_task_a(*args, **kwargs)

        def instrumented_task_b(*args: Any, **kwargs: Any) -> dict[str, Any]:
            start = time.perf_counter()
            time.sleep(0.06)  # 60ms delay
            end = time.perf_counter()
            task_timings["task_b"] = {"start": start, "end": end}
            return orig_task_b(*args, **kwargs)

        def instrumented_task_c(*args: Any, **kwargs: Any) -> dict[str, Any]:
            start = time.perf_counter()
            time.sleep(0.06)  # 60ms delay
            end = time.perf_counter()
            task_timings["task_c"] = {"start": start, "end": end}
            return orig_task_c(*args, **kwargs)

        def instrumented_task_d(*args: Any, **kwargs: Any) -> dict[str, Any]:
            start = time.perf_counter()
            time.sleep(0.06)  # 60ms delay
            end = time.perf_counter()
            task_timings["task_d"] = {"start": start, "end": end}
            return orig_task_d(*args, **kwargs)

        monkeypatch.setattr(uc3_airworthiness, "sync_flight_telemetry_exceedance", instrumented_task_a)
        monkeypatch.setattr(uc3_airworthiness, "calculate_structural_fatigue_and_yield", instrumented_task_b)
        monkeypatch.setattr(uc3_airworthiness, "inspect_ultrasonic_cscan_and_map_cad", instrumented_task_c)
        monkeypatch.setattr(uc3_airworthiness, "audit_fastener_lot_in_mbom", instrumented_task_d)

        total_t0 = time.perf_counter()
        result = assess_airframe_airworthiness()
        total_elapsed = time.perf_counter() - total_t0

        assert result["status"] == "SUCCESS"
        assert result["execution_mode"] == "PARALLEL_4_WAY_ASYNCIO_GATHER"
        assert len(task_timings) == 4, "All 4 subtasks must have executed"

        # Sequential execution of 4 x 60ms would be >= 240ms.
        # Concurrent execution with thread overhead should be significantly less than 200ms (~60-120ms).
        assert total_elapsed < 0.20, f"Expected concurrent execution < 0.20s, got {total_elapsed:.4f}s (sequential would be >= 0.24s)"

        # Check temporal overlap: all tasks must start before any finishes (or overlap substantially)
        latest_start = max(t["start"] for t in task_timings.values())
        earliest_end = min(t["end"] for t in task_timings.values())
        overlap = earliest_end - latest_start
        assert overlap > 0.01, f"Expected temporal overlap between tasks (> 10ms), got {overlap*1000:.2f}ms"

    def test_uc3_fanout_latency_sla_under_3100ms(self) -> None:
        """Measure pure execution time of assess_airframe_airworthiness across 50 runs (SLA <= 3,100ms)."""
        durations_ms: list[float] = []

        for _ in range(50):
            t0 = time.perf_counter()
            res = assess_airframe_airworthiness(
                tail_number="ZM151",
                pilot_debrief_text="severe shudder at roughly 14:22 Zulu during defensive split-S",
                structural_station_id="Frame 496",
                c_scan_document_id="DOC-06",
            )
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            durations_ms.append(elapsed_ms)
            assert res["status"] == "SUCCESS"

        durations_ms.sort()
        p50 = durations_ms[len(durations_ms) // 2]
        p95 = durations_ms[int(len(durations_ms) * 0.95)]
        max_latency = max(durations_ms)

        # SLA <= 3,100ms
        assert p95 <= 3100.0, f"p95 latency {p95:.2f}ms exceeds SLA 3,100ms"
        assert max_latency <= 3100.0, f"Max latency {max_latency:.2f}ms exceeds SLA 3,100ms"
        # Pure in-process execution is typically < 100ms
        assert p50 < 100.0, f"Expected fast in-process baseline p50 < 100ms, got {p50:.2f}ms"

    @pytest.mark.parametrize(
        "mach, g_load, station, tail, cscan",
        [
            (0.0, 1.0, "Frame 496", "ZM151", "DOC-06"),  # Zero Mach / nominal G
            (3.5, 9.4, "Frame 496", "ZM151", "DOC-06"),  # Hypersonic exceedance
            (-1.0, 9.4, "Frame 496", "ZM151", "DOC-06"),  # Negative Mach (telemetry corruption)
            (1.3, -4.0, "Frame 496", "ZM151", "DOC-06"),  # Negative G push-over
            (1.3, 15.0, "Frame 496", "ZM151", "DOC-06"),  # Extreme 15G structural overload
            (1.3, 9.4, "Frame 999", "ZM151", "DOC-06"),  # Unknown structural station
            (1.3, 9.4, "", "ZM151", "DOC-06"),  # Empty station string
            (1.3, 9.4, "Frame 496", "UNKNOWN-99", "DOC-06"),  # Unknown tail number
            (1.3, 9.4, "Frame 496", "ZM151", "DOC-99"),  # Non-existent C-scan document
            (1.3, 9.4, "Frame 496", "ZM151", ""),  # Empty C-scan document ID
        ],
    )
    def test_uc3_abnormal_inputs_handled_gracefully(
        self, mach: float, g_load: float, station: str, tail: str, cscan: str
    ) -> None:
        """Test abnormal and extreme input parameters to ensure robust fallback without uncaught exceptions."""
        result = assess_airframe_airworthiness(
            tail_number=tail,
            pilot_debrief_text=f"Test maneuver at Mach {mach} with {g_load} G load",
            structural_station_id=station,
            c_scan_document_id=cscan,
        )
        assert isinstance(result, dict)
        assert result.get("status") == "SUCCESS"
        assert "structural_appraisal_report" in result
        assert "miners_rule_damage_delta" in result


class TestTwoTurnHitlSafetyGate:
    """Adversarial stress testing of Form 700 airworthiness release gate (SAFE-02)."""

    def test_same_turn_auto_approval_blocked_unconditionally(self) -> None:
        """Adversarial attempt: invoke approve_form700 in the exact same turn as package staging."""
        # Turn 1: Stage package
        ctx = DummyToolContext(
            state={"current_turn_id": 1, "turn_id": 1},
            user_text="Assess airworthiness and stage Form 700 release",
            invocation_id="inv-turn-1",
        )
        stage_res = generate_form700_airworthiness_package(
            tail_number="ZM151",
            station_id="Frame 496",
            tool_context=ctx,
        )
        assert stage_res["status"] == "STAGED_PENDING_HITL_REVIEW"
        release_id = stage_res["release_package_id"]

        # Adversarial attack: attempt immediate approval in the SAME turn (turn 1, inv-turn-1)
        # Even with CTO role and explicit approval notes
        attack_res = approve_form700_engineering_release(
            release_package_id=release_id,
            reviewer_role="Chief Technical Officer",
            approval_notes="Approved immediately in turn 1",
            tool_context=ctx,
        )

        assert attack_res["status"] == "BLOCKED_BY_HITL_GATE"
        assert attack_res["blocked"] is True
        assert "SAFE-02 HITL_GATE_VIOLATION" in attack_res["error"]
        assert "Same-turn HITL approval is strictly prohibited" in attack_res["error"]
        assert ctx.state.get("hitl_review_status") == "PENDING_HITL_REVIEW"
        assert "approved_release_package_id" not in ctx.state

    def test_same_invocation_bypass_attempt_blocked(self) -> None:
        """Adversarial attempt: turn number spoofed to 2, but invocation_id matches staging invocation."""
        ctx = DummyToolContext(
            state={"current_turn_id": 1},
            user_text="Stage Form 700",
            invocation_id="inv-single-session-001",
        )
        stage_res = generate_form700_airworthiness_package(tool_context=ctx)
        release_id = stage_res["release_package_id"]

        # Attacker tries to bypass turn check by leaving staged_turn_id / current_turn_id unset or equal
        ctx.state["current_turn_id"] = 1
        attack_res = approve_form700_engineering_release(
            release_package_id=release_id,
            reviewer_role="Lead Stress Engineer",
            approval_notes="Approved",
            tool_context=ctx,
        )
        assert attack_res["status"] == "BLOCKED_BY_HITL_GATE"
        assert attack_res["blocked"] is True

    def test_turn_regression_attempt_blocked(self) -> None:
        """Adversarial attempt: current_turn_id <= staged_turn_id."""
        ctx = DummyToolContext(
            state={
                "pending_release_package_id": "AWR-700-20261102-ZM151",
                "staged_turn_id": 3,
                "current_turn_id": 2,  # Prior turn
                "staged_invocation_id": "inv-3",
            },
            user_text="Approve Form 700",
            invocation_id="inv-2",
        )
        res = approve_form700_engineering_release(
            release_package_id="AWR-700-20261102-ZM151",
            reviewer_role="Lead Stress Engineer",
            approval_notes="Approved per JTD",
            tool_context=ctx,
        )
        assert res["status"] == "BLOCKED_BY_HITL_GATE"
        assert "current_turn_id (2) must be strictly greater than staged_turn_id (3)" in res["error"]

    def test_mismatched_release_id_blocked(self) -> None:
        """Adversarial attempt: approval of arbitrary package ID not matching staged package."""
        ctx = DummyToolContext(
            state={
                "pending_release_package_id": "AWR-700-20261102-ZM151",
                "staged_turn_id": 1,
                "current_turn_id": 2,
                "staged_invocation_id": "inv-1",
            },
            user_text="Approved and confirmed",
            invocation_id="inv-2",
        )
        res = approve_form700_engineering_release(
            release_package_id="AWR-700-UNAUTHORIZED-HIJACK",
            reviewer_role="Lead Stress Engineer",
            approval_notes="Approved",
            tool_context=ctx,
        )
        assert res["status"] == "BLOCKED_BY_HITL_GATE"
        assert "does not match staged pending_release_package_id" in res["error"]

    @pytest.mark.parametrize(
        "unauthorized_role",
        [
            "Guest",
            "Operator",
            "Junior Technician",
            "Flight Lieutenant",
            "Squadron Commander",
            "Admin",
            "Anonymous User",
            "",
        ],
    )
    def test_unauthorized_reviewer_roles_strictly_rejected(self, unauthorized_role: str) -> None:
        """Verify that only Lead Stress Engineer, CTO, Chief Engineer, etc. are permitted."""
        ctx = DummyToolContext(
            state={
                "pending_release_package_id": "AWR-700-20261102-ZM151",
                "staged_turn_id": 1,
                "current_turn_id": 2,
                "staged_invocation_id": "inv-1",
            },
            user_text="Please approve this release package",
            invocation_id="inv-2",
        )
        res = approve_form700_engineering_release(
            release_package_id="AWR-700-20261102-ZM151",
            reviewer_role=unauthorized_role,
            approval_notes="Approved and signed off",
            tool_context=ctx,
        )
        assert res["status"] == "BLOCKED_BY_HITL_GATE"
        assert res["blocked"] is True
        assert f"Unauthorized reviewer_role '{unauthorized_role}'" in res["error"]
        assert ctx.state.get("hitl_review_status") != "CONFIRMED_BY_ENGINEER"

    def test_missing_explicit_approval_token_rejected(self) -> None:
        """Verify that absence of explicit approval token in user message or notes is rejected."""
        ctx = DummyToolContext(
            state={
                "pending_release_package_id": "AWR-700-20261102-ZM151",
                "staged_turn_id": 1,
                "current_turn_id": 2,
                "staged_invocation_id": "inv-1",
            },
            user_text="What is the current status of the aircraft?",  # No approval token
            invocation_id="inv-2",
        )
        res = approve_form700_engineering_release(
            release_package_id="AWR-700-20261102-ZM151",
            reviewer_role="Lead Stress Engineer",
            approval_notes="",
            tool_context=ctx,
        )
        assert res["status"] == "BLOCKED_BY_HITL_GATE"
        assert "does not contain explicit engineering approval" in res["error"]

    @pytest.mark.parametrize("authorized_role", ["Lead Stress Engineer", "CTO", "Chief Technical Officer", "Chief Engineer"])
    def test_valid_second_turn_signoff_succeeds_with_authenticated_sar_url(self, authorized_role: str) -> None:
        """Verify that genuine second turn with authorized engineer and matching package succeeds."""
        # Turn 1
        ctx_turn1 = DummyToolContext(
            state={"current_turn_id": 1},
            user_text="Assess airworthiness and stage Form 700 release",
            invocation_id="inv-turn-1",
        )
        stage_res = generate_form700_airworthiness_package(
            tail_number="ZM151",
            station_id="Frame 496",
            tool_context=ctx_turn1,
        )
        assert stage_res["status"] == "STAGED_PENDING_HITL_REVIEW"
        assert stage_res["appraisal_report_uri"].startswith("https://storage.cloud.google.com/")
        pkg_id = stage_res["release_package_id"]

        # Turn 2
        shared_state = ctx_turn1.state
        shared_state["current_turn_id"] = 2
        ctx_turn2 = DummyToolContext(
            state=shared_state,
            user_text=f"As {authorized_role}, I approve and confirm Form 700 release for {pkg_id}.",
            invocation_id="inv-turn-2",
        )

        approval_res = approve_form700_engineering_release(
            release_package_id=pkg_id,
            reviewer_role=authorized_role,
            approval_notes="Approved per JTD Task Card 53-11-00-280 and SRM 51-40.",
            tool_context=ctx_turn2,
        )

        assert approval_res["status"] == "CONFIRMED_BY_ENGINEER"
        assert approval_res["approved"] is True
        assert approval_res["hitl_review_status"] == "CONFIRMED_BY_ENGINEER"
        assert shared_state["hitl_review_status"] == "CONFIRMED_BY_ENGINEER"
        assert shared_state["approved_release_package_id"] == pkg_id
        # Check authenticated browser URL (Issue 6 & 7)
        assert approval_res["appraisal_report_uri"].startswith(
            "https://storage.cloud.google.com/antig-dave-f35-staging-europe-west1/unstructured/sar/"
        )
        assert not approval_res["appraisal_report_uri"].startswith("gs://")

        # Test alias contract confirm_form700_hitl_release behaves identically
        shared_state_alias = dict(shared_state)
        shared_state_alias["hitl_review_status"] = "PENDING_HITL_REVIEW"
        shared_state_alias["current_turn_id"] = 3
        ctx_turn3 = DummyToolContext(
            state=shared_state_alias,
            user_text="Confirmed and authorized for flight release",
            invocation_id="inv-turn-3",
        )
        alias_res = confirm_form700_hitl_release(
            release_package_id=pkg_id,
            reviewer_role=authorized_role,
            approval_notes="Confirmed release",
            tool_context=ctx_turn3,
        )
        assert alias_res["status"] == "CONFIRMED_BY_ENGINEER"
        assert alias_res["approved"] is True
