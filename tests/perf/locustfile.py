"""Locust Load Test Script for F-35 Fleet Sustainment Agent (Standard Flight-Line Profile).

Simulates 10 concurrent flight-line maintenance engineers submitting mixed
UC1, UC2, UC3, and Fast-Path queries (40% UC2, 35% UC1, 20% UC3, 5% Fast-Path)
against the F-35 Sustainment Agent HTTP Gateway backed by live EU BigQuery
(`antig-dave.ukd_f35_sustainment_demo`) and EU Discovery Engine
(`ukd-f35-jtd-ietm-ds` & `ukd-f35-narrative-logs-ds`).

Usage:
    locust -f tests/perf/locustfile.py --headless -u 10 -r 2 --run-time 5m --host http://127.0.0.1:8089 --csv tests/perf/results/locust_flightline
"""

from __future__ import annotations

import os
from locust import HttpUser, between, task


class FlightLineMaintenanceUser(HttpUser):
    """Simulates a flight-line maintenance engineer at RAF Marham / HMS Queen Elizabeth."""

    # Realistic flight-line query cadence (1.5s to 3.5s between engineer actions)
    wait_time = between(1.5, 3.5)

    def on_start(self) -> None:
        """Initialize user session headers."""
        self.headers = {
            "Content-Type": "application/json",
            "X-FlightLine-Squadron": os.environ.get("F35_SQUADRON", "617-SQN-MARHAM"),
        }

    @task(8)
    def query_uc2_jtd_manuals(self) -> None:
        """UC2 (40% workload): Technician troubleshooting sticky canopy latch without BIT faults."""
        payload = {
            "scenario": "UC2_JTD_SEARCH",
            "symptom_query": "Canopy latch stiff during pre-flight on ZM151 without BIT faults. Lubrication and rigging specs?",
            "bit_fault_present": False,
            "subsystem_filter": "53-30",
        }
        with self.client.post(
            "/v1/sustainment/uc2/search",
            json=payload,
            headers=self.headers,
            catch_response=True,
            name="TC-LP-03_UC2_JTD_Search",
        ) as resp:
            if resp.status_code == 200 and "citations" in resp.text:
                resp.success()
            else:
                resp.failure(f"UC2 Search Failed: {resp.status_code} - {resp.text[:120]}")

    @task(7)
    def query_uc1_supply_analytics(self) -> None:
        """UC1 (35% workload): Flight-line chief checking actuator fatigue, depot stock & tail swap."""
        payload = {
            "scenario": "UC1_SUPPLY_ANALYTICS",
            "base_location": "RAF Marham",
            "hours_to_limit_window": 50.0,
            "sortie_id": "SRT-MAR-20261103-01",
            "primary_tail": "ZM151",
            "spare_tail": "ZM154",
        }
        with self.client.post(
            "/v1/sustainment/uc1/analytics",
            json=payload,
            headers=self.headers,
            catch_response=True,
            name="TC-LP-02_UC1_Supply_Analytics",
        ) as resp:
            if resp.status_code == 200 and "actuator_fatigue_threshold_chart" in resp.text:
                resp.success()
            else:
                resp.failure(f"UC1 Analytics Failed: {resp.status_code} - {resp.text[:120]}")

    @task(4)
    def query_uc3_airworthiness_exceedance(self) -> None:
        """UC3 (20% workload): Airworthiness engineer running 4-way ASIP fan-out & Form 700 HITL."""
        payload = {
            "scenario": "UC3_AIRWORTHINESS_FANOUT",
            "tail_number": "ZM151",
            "pilot_debrief_text": "severe shudder at 14:22 Zulu during defensive split-S",
            "structural_station_id": "Frame 496",
            "c_scan_document_id": "DOC-06",
        }
        with self.client.post(
            "/v1/sustainment/uc3/airworthiness",
            json=payload,
            headers=self.headers,
            catch_response=True,
            name="TC-LP-04_UC3_Airworthiness_FanOut",
        ) as resp:
            if resp.status_code == 200 and "structural_appraisal_report" in resp.text:
                resp.success()
            else:
                resp.failure(f"UC3 Airworthiness Failed: {resp.status_code} - {resp.text[:120]}")

    @task(1)
    def fast_path_status(self) -> None:
        """Fast-Path (5% workload): Instant Tier 1/2 health/status check (< 10 ms)."""
        payload = {"message": "status"}
        with self.client.post(
            "/v1/sustainment/fastpath",
            json=payload,
            headers=self.headers,
            catch_response=True,
            name="TC-LP-01_FastPath_Status",
        ) as resp:
            if resp.status_code == 200 and "operational" in resp.text.lower():
                resp.success()
            else:
                resp.failure(f"FastPath Status Failed: {resp.status_code}")
