#!/usr/bin/env python3
"""E2E Test Suite Runner for F-35 Fleet Sustainment Agent Platform (`f35-sustainment-agent`).

Usage:
    uv run python tests/e2e/run_e2e_suite.py --tier all
    uv run python tests/e2e/run_e2e_suite.py --tier 1
    uv run python tests/e2e/run_e2e_suite.py --tier 2
    uv run python tests/e2e/run_e2e_suite.py --tier 3
    uv run python tests/e2e/run_e2e_suite.py --tier 4
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pytest

E2E_DIR = Path(__file__).resolve().parent

TIER_MAP: dict[str, list[str]] = {
    "1": [str(E2E_DIR / "test_tier1_feature_coverage.py")],
    "2": [str(E2E_DIR / "test_tier2_boundary_corner.py")],
    "3": [str(E2E_DIR / "test_tier3_cross_feature.py")],
    "4": [str(E2E_DIR / "test_tier4_real_world_scenarios.py")],
    "all": [
        str(E2E_DIR / "test_tier1_feature_coverage.py"),
        str(E2E_DIR / "test_tier2_boundary_corner.py"),
        str(E2E_DIR / "test_tier3_cross_feature.py"),
        str(E2E_DIR / "test_tier4_real_world_scenarios.py"),
    ],
}


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and execute the selected E2E tier(s) via pytest."""
    parser = argparse.ArgumentParser(
        description="Run the 4-Tier E2E Test Suite for f35-sustainment-agent."
    )
    parser.add_argument(
        "--tier",
        choices=("1", "2", "3", "4", "all"),
        default="all",
        help="Select E2E tier to execute (1, 2, 3, 4, or all).",
    )
    args, extra_pytest_args = parser.parse_known_args(argv)
    targets = TIER_MAP[args.tier]
    pytest_args = ["-v", *targets, *extra_pytest_args]
    return int(pytest.main(pytest_args))


if __name__ == "__main__":
    sys.exit(main())
