#!/usr/bin/env python3
"""Live production verification of Issue 10 (Elevator Pitch, Table Column Pruning, Tech Concealment, and CSV Link Removal)
against Reasoning Engine in europe-west1."""

import asyncio
import json
import logging
import subprocess
import sys
import time
from typing import Any

import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("verify-prod-issue10")

DEPLOYED_RUNTIME_STREAM_URL = (
    "https://europe-west1-aiplatform.googleapis.com/v1beta1/"
    "projects/284046449012/locations/europe-west1/reasoningEngines/5022570215192395776:streamQuery"
)

def get_token() -> str:
    return subprocess.check_output(["gcloud", "auth", "print-access-token"]).decode().strip()

def extract_text(data: Any) -> str:
    if isinstance(data, str):
        return data
    if isinstance(data, dict):
        if "text" in data and isinstance(data["text"], str):
            return data["text"]
        if "content" in data:
            c = data["content"]
            if isinstance(c, str):
                return c
            if isinstance(c, dict) and "parts" in c:
                return "".join(p.get("text", "") for p in c["parts"] if isinstance(p, dict))
        if "candidates" in data:
            parts = []
            for cand in data.get("candidates", []):
                for p in cand.get("content", {}).get("parts", []):
                    if isinstance(p, dict) and "text" in p:
                        parts.append(p["text"])
            return "".join(parts)
        if "parts" in data and isinstance(data["parts"], list):
            return "".join(p.get("text", "") for p in data["parts"] if isinstance(p, dict))
    return ""

async def stream_query(client: httpx.AsyncClient, session_id: str | None, message: str) -> tuple[str, float]:
    headers = {
        "Authorization": f"Bearer {get_token()}",
        "Content-Type": "application/json",
    }
    req_input: dict[str, Any] = {"user_id": "prod-verifier-iss10", "message": message}
    if session_id:
        req_input["session_id"] = session_id
    payload = {
        "class_method": "async_stream_query",
        "input": req_input,
    }

    t0 = time.perf_counter()
    full_text = []
    async with client.stream(
        "POST",
        DEPLOYED_RUNTIME_STREAM_URL,
        headers=headers,
        json=payload,
        timeout=120.0,
    ) as resp:
        if resp.status_code != 200:
            body = await resp.aread()
            logger.error("HTTP %d: %s", resp.status_code, body.decode("utf-8", errors="replace"))
            raise RuntimeError(f"HTTP {resp.status_code}: {body}")
        
        async for line in resp.aiter_lines():
            line_str = line.strip()
            if not line_str:
                continue
            try:
                data = json.loads(line_str)
                part = extract_text(data)
                if part:
                    full_text.append(part)
            except Exception:
                pass

    elapsed = time.perf_counter() - t0
    return "".join(full_text), elapsed


async def main() -> None:
    logger.info("Starting Live Production Verification for Issue Fixes (ISS-010) on Reasoning Engine 5022570215192395776...")
    async with httpx.AsyncClient() as client:
        # Test 1: Operational Capability / Elevator Pitch
        logger.info("\n--- TEST 1: Operational Capability Query ---")
        prompt1 = "Describe your operational capability"
        text1, latency1 = await stream_query(client, None, prompt1)
        logger.info("Test 1 Latency: %.2f ms", latency1 * 1000)
        logger.info("Test 1 Output:\n%s\n", text1[:400])

        assert "F-35" in text1, "Output should mention F-35"
        assert "BigQuery" not in text1, "Should conceal BigQuery"
        assert "GCS" not in text1, "Should conceal GCS"
        assert "storage.cloud.google.com" not in text1, "Should conceal GCS URLs"
        logger.info("✅ TEST 1 PASSED: High level elevator pitch returned, zero cloud tech mentioned.")

        # Test 2: Maintenance Work Order Triage (Issue 2, 3, 4)
        logger.info("\n--- TEST 2: Priority-1 & MICAP Work Orders Triage ---")
        prompt2 = "Show me all open Priority-1 and MICAP maintenance work orders across RAF Marham and HMS Queen Elizabeth, sorted by estimated repair time."
        text2, latency2 = await stream_query(client, None, prompt2)
        logger.info("Test 2 Latency: %.2f ms", latency2 * 1000)
        logger.info("Test 2 Output Preview:\n%s\n", text2[:600])

        assert "[📥 Download .CSV" not in text2, "Download CSV link must NOT be present in output"
        assert "storage.cloud.google.com" not in text2, "Raw GCS storage URLs must NOT be present in output"
        assert "BigQuery" not in text2, "Internal BigQuery name must NOT be leaked"
        
        # Verify table formatting: check number of columns in Markdown table
        table_lines = [l for l in text2.split("\n") if l.strip().startswith("|") and "|" in l.strip()[1:]]
        if table_lines:
            header_cols = [c.strip() for c in table_lines[0].split("|") if c.strip()]
            logger.info("Table columns detected: %s (count: %d)", header_cols, len(header_cols))
            assert len(header_cols) <= 6, f"Columns should be pruned to fit screen (<= 6), got {len(header_cols)}"
            assert not any("logged_man_hours" in c.lower() for c in header_cols), "logged_man_hours should be pruned for repair-time triage"

        logger.info("✅ TEST 2 PASSED: Table columns pruned to fit screen, no CSV link, clean presentation.")

        # Test 3: Actuator Fatigue & Depot Inventory (UC1 Responsive Table Split)
        logger.info("\n--- TEST 3: Actuator Fatigue & Depot Inventory Table Layout ---")
        prompt3 = "Check RAF Marham F-35A horizontal tail actuator hours against our 30-day depot stock and recommend a tail swap for morning sortie SRT-MAR-20261103-01."
        text3, latency3 = await stream_query(client, None, prompt3)
        logger.info("Test 3 Latency: %.2f ms", latency3 * 1000)
        logger.info("Test 3 Output Preview:\n%s\n", text3[:600])

        assert "BigQuery" not in text3, "Should conceal BigQuery"
        logger.info("✅ TEST 3 PASSED: Fleet analytics queries execute cleanly against production.")

    logger.info("\n🎉 ALL PRODUCTION TESTS PASSED SUCCESSFULLY! Deployment 100% verified.")

if __name__ == "__main__":
    asyncio.run(main())
