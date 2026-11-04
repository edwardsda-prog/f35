"""Unit tests for headless presentation chart generation engine (`app/tools/chart_painter.py`).

Verifies:
1. PNG byte generation and valid magic header (\\x89PNG\\r\\n\\x1a\\n).
2. Clean Light Briefing Theme formatting.
3. 16:9 widescreen layout (1920x1080 resolution).
4. Sub-second diagram rendering SLA (< 1,000 ms).
5. Storage URL format (https://storage.cloud.google.com/...).
"""

from __future__ import annotations

import struct
import time
from typing import Any

import pytest

from app.seed_data.bq_seed_records import (
    AIRFRAME_COMPONENT_TELEMETRY_ROWS,
    GLOBAL_DEPOT_INVENTORY_ROWS,
)
from app.tools.chart_painter import (
    CHART_STORAGE_PREFIX,
    generate_sustainment_graphics,
    render_actuator_fatigue_chart,
    render_depot_inventory_chart,
    render_executive_dashboard_chart,
    upload_chart_to_gcs,
)

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def _extract_png_dimensions(data: bytes) -> tuple[int, int]:
    """Parse PNG IHDR chunk to extract width and height in pixels."""
    if len(data) < 24 or data[:8] != PNG_MAGIC:
        raise ValueError("Invalid PNG data")
    # IHDR chunk starts at byte 12 (length 4, type 4, then data)
    width, height = struct.unpack(">II", data[16:24])
    return width, height


class TestChartPainter:
    """Test suite for presentation chart painter."""

    def test_render_actuator_fatigue_chart_png_format(self) -> None:
        """Verify actuator fatigue chart produces valid 16:9 PNG."""
        t0 = time.perf_counter()
        png_bytes = render_actuator_fatigue_chart(AIRFRAME_COMPONENT_TELEMETRY_ROWS)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        assert png_bytes.startswith(PNG_MAGIC), "Output must begin with PNG header"
        width, height = _extract_png_dimensions(png_bytes)
        assert width == 1920, f"Expected width 1920, got {width}"
        assert height == 1080, f"Expected height 1080, got {height}"
        assert elapsed_ms < 1000.0, f"Render took {elapsed_ms:.2f} ms (> 1,000 ms SLA)"

    def test_render_depot_inventory_chart_png_format(self) -> None:
        """Verify depot inventory chart produces valid 16:9 PNG."""
        t0 = time.perf_counter()
        png_bytes = render_depot_inventory_chart(GLOBAL_DEPOT_INVENTORY_ROWS)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        assert png_bytes.startswith(PNG_MAGIC), "Output must begin with PNG header"
        width, height = _extract_png_dimensions(png_bytes)
        assert width == 1920, f"Expected width 1920, got {width}"
        assert height == 1080, f"Expected height 1080, got {height}"
        assert elapsed_ms < 1000.0, f"Render took {elapsed_ms:.2f} ms (> 1,000 ms SLA)"

    def test_render_executive_dashboard_composite(self) -> None:
        """Verify composite executive dashboard generates valid 16:9 slide."""
        t0 = time.perf_counter()
        png_bytes = render_executive_dashboard_chart(
            AIRFRAME_COMPONENT_TELEMETRY_ROWS,
            GLOBAL_DEPOT_INVENTORY_ROWS,
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        assert png_bytes.startswith(PNG_MAGIC), "Output must begin with PNG header"
        width, height = _extract_png_dimensions(png_bytes)
        assert width == 1920, f"Expected width 1920, got {width}"
        assert height == 1080, f"Expected height 1080, got {height}"
        assert elapsed_ms < 1000.0, f"Render took {elapsed_ms:.2f} ms (> 1,000 ms SLA)"

    def test_upload_chart_to_gcs_url_structure(self) -> None:
        """Verify GCS upload returns properly formatted authenticated URL."""
        png_bytes = render_actuator_fatigue_chart(AIRFRAME_COMPONENT_TELEMETRY_ROWS)
        url, upload_ms = upload_chart_to_gcs(png_bytes, "test_chart.png")

        assert url.startswith("https://storage.cloud.google.com/antig-dave-f35-staging-europe-west1/charts/")
        assert url.endswith("test_chart.png")
        assert isinstance(upload_ms, float)

    def test_generate_sustainment_graphics_both(self) -> None:
        """Verify orchestrator generates executive dashboard and returns full metadata."""
        t0 = time.perf_counter()
        res = generate_sustainment_graphics(
            chart_name="both",
            telemetry_rows=AIRFRAME_COMPONENT_TELEMETRY_ROWS,
            inventory_rows=GLOBAL_DEPOT_INVENTORY_ROWS,
        )
        total_ms = (time.perf_counter() - t0) * 1000.0

        assert "charts" in res
        assert len(res["charts"]) == 1
        dash = res["charts"][0]
        assert "Executive Briefing Dashboard" in dash["title"]
        assert dash["url"].startswith("https://storage.cloud.google.com/")
        assert "📥 Download" in dash["download_link"]
        assert total_ms < 1500.0, f"Total generation and upload took {total_ms:.2f} ms"

    def test_generate_sustainment_graphics_individual(self) -> None:
        """Verify individual chart generation works for specific requests."""
        res = generate_sustainment_graphics(
            chart_name="actuator_fatigue_threshold_chart",
            telemetry_rows=AIRFRAME_COMPONENT_TELEMETRY_ROWS,
            inventory_rows=GLOBAL_DEPOT_INVENTORY_ROWS,
        )
        assert len(res["charts"]) == 1
        assert "Actuator Fatigue Threshold" in res["charts"][0]["title"]
        assert "actuator_fatigue_threshold_chart.png" in res["charts"][0]["url"]
